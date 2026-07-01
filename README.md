# Format Changer

A lightweight web-based file converter for switching files between common formats across different format families.

Format Changer helps users convert images, documents, audio, video, archives, and data files through a simple and modern interface. The project is designed to make format conversion quick, visual, and easy to explore without needing manual command-line tools.

## Description

Format Changer is a FastAPI application with a simple browser-based UI for transforming files into compatible formats. It focuses on format families rather than complicated workflows, so users can quickly choose a source file, select a target format, and download the converted result.

## Features

- Convert files across multiple format categories
- Support for images, documents, audio, video, archives, and data files
- Simple upload and conversion flow with a clean interface
- Format-aware selection for compatible target formats
- Download-ready converted files directly from the browser
- Easy to extend with new conversion categories and formats

## Tech Stack

### Backend
- Python
- FastAPI
- Jinja2 templates
- Python multipart uploads

### Frontend
- HTML
- CSS
- JavaScript

### Other
- Static file serving for styling and assets
- Browser-based upload and download flow

## Project Structure

```text
format_changer/
├── backend/
│   ├── app_config.py
│   ├── converter_config.py
│   ├── convert_func.py
│   ├── main.py
│   └── __init__.py
├── static/
│   └── styles.css
├── templates/
│   ├── base.html
│   ├── convert.html
│   ├── convert_category.html
│   └── ...
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/format_changer.git
   cd format_changer
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Run the Application

Start the development server with:

```bash
uvicorn backend.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/
```

## Usage

1. Open the home page.
2. Choose a format category such as images, documents, audio, archives, data, or video.
3. Upload a file.
4. Select a target format.
5. Convert the file and download the result.

## Supported Format Families

- Images: PNG, JPG, JPEG, WEBP, BMP, GIF
- Documents: PDF, TXT, DOCX, RTF, ODT, HTML
- Audio: MP3, WAV, OGG, FLAC, AAC, M4A
- Video: MP4, WEBM, AVI, MOV, GIF
- Archives: ZIP, TAR, GZ, 7Z
- Data: JSON, CSV, XML, YAML, TSV

## License

This project is licensed under the MIT License. See the LICENSE file for details.
