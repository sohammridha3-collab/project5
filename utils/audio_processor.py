import glob
import os
import shutil
from typing import Optional


def ensure_ffmpeg_available() -> Optional[str]:
    """Ensure ffmpeg and ffprobe are discoverable by yt-dlp and pydub."""
    # 1. Check if already on current PATH
    ffmpeg_on_path = shutil.which("ffmpeg")
    ffprobe_on_path = shutil.which("ffprobe")
    if ffmpeg_on_path and ffprobe_on_path:
        return os.path.dirname(ffmpeg_on_path)

    # 2. Check WinGet Gyan.FFmpeg installation directory
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        pattern = os.path.join(
            local_app_data, "Microsoft", "WinGet", "Packages", "Gyan.FFmpeg*", "**", "bin"
        )
        matches = glob.glob(pattern, recursive=True)
        for bin_dir in matches:
            ffmpeg_exe = os.path.join(bin_dir, "ffmpeg.exe")
            if os.path.exists(ffmpeg_exe):
                os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
                return bin_dir

    # 3. Check other common installation paths on Windows
    common_paths = [
        r"C:\ffmpeg\bin",
        r"C:\Program Files\ffmpeg\bin",
        r"C:\ProgramData\chocolatey\bin",
    ]
    for bin_dir in common_paths:
        ffmpeg_exe = os.path.join(bin_dir, "ffmpeg.exe")
        if os.path.exists(ffmpeg_exe):
            os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
            return bin_dir

    return None


# Configure PATH before importing AudioSegment or yt_dlp
FFMPEG_DIR = ensure_ffmpeg_available()

import yt_dlp
from pydub import AudioSegment

if FFMPEG_DIR:
    AudioSegment.converter = os.path.join(FFMPEG_DIR, "ffmpeg.exe")
    ffprobe_path = os.path.join(FFMPEG_DIR, "ffprobe.exe")
    if os.path.exists(ffprobe_path):
        AudioSegment.ffprobe = ffprobe_path

DOWNLOAD_DIR = "downloades"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_youtube_audio(url: str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
    }

    # Pass explicit ffmpeg location if discovered
    ffmpeg_location = FFMPEG_DIR or ensure_ffmpeg_available()
    if ffmpeg_location:
        ydl_opts["ffmpeg_location"] = ffmpeg_location

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).replace(".webm", ".wav").replace(".m4a", ".wav")
    return filename


def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)  # 16khz
    audio.export(output_path, format="wav")
    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000

    chunks = []
    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start: start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)

    return chunks


def process_input(source: str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks
