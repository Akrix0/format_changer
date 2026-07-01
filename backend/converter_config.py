from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class ConverterCategory:
    key: str
    title: str
    description: str
    formats: List[str]
    file_accept: str
    placeholder: str = "Choose file"
    supported_from: Dict[str, List[str]] | None = None


CONVERTER_CATEGORIES: Dict[str, ConverterCategory] = {
    "images": ConverterCategory(
        key="images",
        title="Images",
        description="Convert raster images between common formats",
        formats=["PNG", "JPG", "JPEG", "WEBP", "BMP", "GIF"],
        file_accept="image/*",
        placeholder="Choose image"
    ),
    "documents": ConverterCategory(
        key="documents",
        title="Documents",
        description="Convert documents like PDF, TXT, DOCX, RTF, ODT, and HTML",
        formats=["PDF", "TXT", "DOCX", "RTF", "ODT", "HTML"],
        file_accept=".pdf,.doc,.docx,.txt,.rtf,.odt,.html,.htm",
        placeholder="Choose document",
        supported_from={
            "pdf": ["pdf", "txt", "docx", "rtf", "odt", "html"],
            "txt": ["txt", "html"],
            "docx": ["docx", "txt", "html"],
            "rtf": ["rtf", "txt", "html"],
            "odt": ["odt", "txt", "html"],
            "html": ["html", "txt"],
        },
    ),
    "archives": ConverterCategory(
        key="archives",
        title="Archives",
        description="Work with compressed archives such as ZIP, TAR, GZ, and 7Z",
        formats=["ZIP", "TAR", "GZ", "7Z"],
        file_accept=".zip,.tar,.gz,.7z,.tgz",
        placeholder="Choose archive",
        supported_from={
            "zip": ["zip", "tar", "7z"],
            "tar": ["tar", "zip", "gz"],
            "gz": ["gz", "tar"],
            "tgz": ["tgz", "tar"],
            "7z": ["7z", "zip"],
        },
    ),
    "audio": ConverterCategory(
        key="audio",
        title="Audio",
        description="Convert audio tracks between common audio formats",
        formats=["MP3", "WAV", "OGG", "FLAC", "AAC", "M4A"],
        file_accept="audio/*",
        placeholder="Choose audio",
        supported_from={
            "mp3": ["mp3", "wav", "ogg", "flac", "aac", "m4a"],
            "wav": ["wav", "mp3", "ogg", "flac", "aac", "m4a"],
            "ogg": ["ogg", "mp3", "wav", "flac", "aac", "m4a"],
            "flac": ["flac", "mp3", "wav", "ogg", "aac", "m4a"],
            "aac": ["aac", "mp3", "wav", "ogg", "flac", "m4a"],
            "m4a": ["m4a", "mp3", "wav", "ogg", "flac", "aac"],
        },
    ),
    "videos": ConverterCategory(
        key="videos",
        title="Videos",
        description="Convert videos into animated GIFs or audio-friendly outputs",
        formats=["MP4", "WEBM", "AVI", "MOV", "GIF", "MP3", "WAV", "OGG"],
        file_accept="video/*",
        placeholder="Choose video",
        supported_from={
            "mp4": ["mp4", "gif", "mp3", "wav", "ogg"],
            "webm": ["webm", "gif", "mp3", "wav", "ogg"],
            "avi": ["avi", "gif", "mp3", "wav", "ogg"],
            "mov": ["mov", "gif", "mp3", "wav", "ogg"],
            "gif": ["gif"],
            "mp3": ["mp3", "wav", "ogg"],
            "wav": ["wav", "mp3", "ogg"],
            "ogg": ["ogg", "mp3", "wav"],
        },
    ),
    "data": ConverterCategory(
        key="data",
        title="Data",
        description="Convert data files such as JSON, CSV, XML, YAML, and TSV",
        formats=["JSON", "CSV", "XML", "YAML", "YML", "TSV", "TXT"],
        file_accept=".json,.csv,.xml,.yaml,.yml,.tsv,.txt",
        placeholder="Choose data file",
        supported_from={
            "json": ["json", "txt", "csv"],
            "csv": ["csv", "txt", "json"],
            "xml": ["xml", "txt"],
            "yaml": ["yaml", "yml", "txt"],
            "yml": ["yml", "yaml", "txt"],
            "tsv": ["tsv", "txt"],
            "txt": ["txt"],
        },
    ),
}


def get_converter_categories() -> List[ConverterCategory]:
    return list(CONVERTER_CATEGORIES.values())


def get_converter_category(key: str) -> ConverterCategory | None:
    return CONVERTER_CATEGORIES.get(key)


def get_supported_formats(category: ConverterCategory, input_format: str) -> List[str]:
    if not category.supported_from:
        return category.formats

    normalized_input = input_format.lower()
    allowed = category.supported_from.get(normalized_input, [])
    if not allowed:
        return []

    return [fmt for fmt in category.formats if fmt.lower() in allowed]
