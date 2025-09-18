import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

import yt_dlp

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)


# Serve frontend HTML
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


# Video metadata
@app.get("/info/")
async def get_info(url: str = Query(...)):
    try:
        ydl_opts = {"quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        return {
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "url": url,
        }
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# Download video
@app.get("/download/")
async def download_video(url: str = Query(...)):
    try:
        ydl_opts = {
            "quiet": True,
            "merge_output_format": "mp4",
            "outtmpl": os.path.join(DOWNLOADS_DIR, "%(title)s.%(ext)s"),
            "format": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace(".webm", ".mp4")

        if not os.path.exists(filename):
            return JSONResponse({"error": "Download failed"}, status_code=500)

        return FileResponse(filename, media_type="video/mp4", filename=os.path.basename(filename))

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
