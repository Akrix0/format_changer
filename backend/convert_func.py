import csv
import gzip
import json
import shutil
import subprocess
import tarfile
import tempfile
import zipfile
from html import escape
from pathlib import Path
from typing import Tuple

from PIL import Image
from fastapi import UploadFile


IMAGE_FORMATS = {"png", "jpg", "jpeg", "webp", "gif", "bmp"}
AUDIO_FORMATS = {"mp3", "wav", "ogg", "flac", "aac", "m4a"}
VIDEO_FORMATS = {"mp4", "webm", "avi", "mov", "gif"}


def _normalize_format(value: str) -> str:
    return (value or "").strip().lower()


def convert_uploaded_file(upload_file: UploadFile, category_key: str, target_format: str) -> Tuple[bytes, str]:
    source_name = upload_file.filename or "upload.bin"
    source_ext = Path(source_name).suffix.lower().lstrip(".") or "bin"
    target_ext = _normalize_format(target_format)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        input_path = tmp_path / f"input.{source_ext}"
        output_path = tmp_path / f"output.{target_ext}"

        with input_path.open("wb") as handle:
            shutil.copyfileobj(upload_file.file, handle)

        if category_key == "images":
            _convert_image(input_path, output_path, target_ext)
        elif category_key in {"audio", "videos"}:
            _convert_media(input_path, output_path, target_ext, category_key)
        elif category_key == "archives":
            _convert_archive(input_path, output_path, target_ext)
        elif category_key == "data":
            _convert_data(input_path, output_path, target_ext)
        elif category_key == "documents":
            _convert_document(input_path, output_path, target_ext)
        else:
            raise ValueError(f"Unsupported category: {category_key}")

        return output_path.read_bytes(), output_path.name


def _convert_image(input_path: Path, output_path: Path, target_format: str) -> None:
    if target_format not in IMAGE_FORMATS:
        raise ValueError(f"Unsupported image target: {target_format}")

    format_map = {
        "png": "PNG",
        "jpg": "JPEG",
        "jpeg": "JPEG",
        "webp": "WEBP",
        "gif": "GIF",
        "bmp": "BMP",
    }

    with Image.open(input_path) as image:
        if target_format in {"jpg", "jpeg"}:
            if image.mode in {"RGBA", "LA", "P", "CMYK"}:
                image = image.convert("RGB")
        elif target_format in {"png", "gif", "bmp", "webp"}:
            if image.mode in {"RGBA", "LA", "P"}:
                image = image.convert("RGBA")
        else:
            image = image.convert("RGBA")

        image.save(output_path, format=format_map[target_format])


def _convert_media(input_path: Path, output_path: Path, target_format: str, category_key: str) -> None:
    if category_key == "videos" and target_format == "gif":
        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-vf",
            "fps=8,scale=480:-1:flags=lanczos",
            str(output_path),
        ]
    elif category_key == "videos" and target_format in {"mp4", "webm", "avi", "mov"}:
        codec_map = {
            "mp4": ("libx264", "yuv420p", "aac"),
            "webm": ("libvpx-vp9", "yuv420p", "libopus"),
            "avi": ("mpeg4", "yuv420p", "mp3"),
            "mov": ("libx264", "yuv420p", "aac"),
        }
        codec_v, pix_fmt, codec_a = codec_map[target_format]
        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-c:v",
            codec_v,
            "-pix_fmt",
            pix_fmt,
            "-c:a",
            codec_a,
            str(output_path),
        ]
    elif category_key == "audio" and target_format in AUDIO_FORMATS:
        codec_map = {
            "mp3": "libmp3lame",
            "wav": "pcm_s16le",
            "ogg": "libvorbis",
            "flac": "flac",
            "aac": "aac",
            "m4a": "aac",
        }
        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-vn",
            "-c:a",
            codec_map[target_format],
            str(output_path),
        ]
    elif category_key == "videos" and target_format in AUDIO_FORMATS:
        codec_map = {
            "mp3": "libmp3lame",
            "wav": "pcm_s16le",
            "ogg": "libvorbis",
            "flac": "flac",
            "aac": "aac",
            "m4a": "aac",
        }
        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-vn",
            "-c:a",
            codec_map[target_format],
            str(output_path),
        ]
    else:
        raise ValueError(f"Unsupported {category_key} target: {target_format}")

    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr or completed.stdout or "Media conversion failed")


def _convert_archive(input_path: Path, output_path: Path, target_format: str) -> None:
    if target_format == "zip":
        with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.write(input_path, arcname=input_path.name)
    elif target_format == "tar":
        with tarfile.open(output_path, "w") as archive:
            archive.add(input_path, arcname=input_path.name)
    elif target_format == "gz":
        with input_path.open("rb") as src, gzip.open(output_path, "wb") as dst:
            shutil.copyfileobj(src, dst)
    elif target_format == "7z":
        shutil.copyfile(input_path, output_path)
    else:
        shutil.copyfile(input_path, output_path)


def _convert_data(input_path: Path, output_path: Path, target_format: str) -> None:
    text = input_path.read_text(encoding="utf-8", errors="ignore")
    target_format = target_format.lower()

    if target_format == "json":
        try:
            data = json.loads(text)
            output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            return
        except Exception:
            pass
    if target_format in {"csv", "tsv"}:
        delimiter = "," if target_format == "csv" else "\t"
        try:
            rows = list(csv.reader(text.splitlines()))
            with output_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle, delimiter=delimiter)
                writer.writerows(rows)
            return
        except Exception:
            pass
    if target_format in {"xml", "html"}:
        output_path.write_text(f"<root>{escape(text)}</root>", encoding="utf-8")
        return
    if target_format in {"yaml", "yml"}:
        output_path.write_text(text, encoding="utf-8")
        return

    output_path.write_text(text, encoding="utf-8")


def _convert_document(input_path: Path, output_path: Path, target_format: str) -> None:
    text = input_path.read_text(encoding="utf-8", errors="ignore")
    target_format = target_format.lower()

    if target_format == "txt":
        output_path.write_text(text, encoding="utf-8")
    elif target_format == "html":
        output_path.write_text(f"<html><body><pre>{escape(text)}</pre></body></html>", encoding="utf-8")
    else:
        output_path.write_text(text, encoding="utf-8")
