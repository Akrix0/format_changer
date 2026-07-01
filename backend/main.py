from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.app_config import STATIC_DIR, TEMPLATES_DIR
from backend.converter_config import get_converter_categories, get_converter_category
from backend.convert_func import convert_uploaded_file

app = FastAPI(title="Format Changer")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/", name="home")
def home(request: Request):
    return RedirectResponse(url=request.url_for("convert_page"), status_code=303)


@app.get("/convert/", name="convert_page")
def convert_page(request: Request):
    return templates.TemplateResponse(
        request,
        "convert.html",
        {"request": request, "categories": get_converter_categories()},
    )


@app.get("/convert/{category_key}/", name="convert_category_page")
def convert_category_page(request: Request, category_key: str):
    category = get_converter_category(category_key)
    if not category:
        return RedirectResponse(url=request.url_for("convert_page"), status_code=303)
    return templates.TemplateResponse(
        request,
        "convert_category.html",
        {"request": request, "category": category},
    )


@app.post("/convert/{category_key}/")
async def convert_file(category_key: str, file: UploadFile = File(...), target_format: str = Form("")):
    category = get_converter_category(category_key)
    if not category:
        raise HTTPException(status_code=404, detail="Unknown category")

    target = (target_format or category.formats[0]).lower()
    data, filename = convert_uploaded_file(file, category_key, target)
    media_type = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "webp": "image/webp",
        "gif": "image/gif",
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "ogg": "audio/ogg",
        "flac": "audio/flac",
        "aac": "audio/aac",
        "m4a": "audio/mp4",
        "mp4": "video/mp4",
        "webm": "video/webm",
        "avi": "video/x-msvideo",
        "mov": "video/quicktime",
        "zip": "application/zip",
        "tar": "application/x-tar",
        "gz": "application/gzip",
        "7z": "application/x-7z-compressed",
        "txt": "text/plain",
        "json": "application/json",
        "csv": "text/csv",
        "xml": "application/xml",
        "yaml": "application/x-yaml",
        "yml": "application/x-yaml",
        "tsv": "text/tab-separated-values",
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "rtf": "text/rtf",
        "odt": "application/vnd.oasis.opendocument.text",
        "html": "text/html",
    }.get(target, "application/octet-stream")

    return StreamingResponse(
        iter([data]),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
