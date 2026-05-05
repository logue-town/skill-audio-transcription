#!/usr/bin/env python3
"""音声・動画ファイルを mlx-whisper でテキストに変換する。"""

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".webm"}
DEFAULT_MODEL = "mlx-community/whisper-large-v3-turbo"


def extract_audio(video_path: Path, tmp_dir: str) -> Path:
    audio_path = Path(tmp_dir) / "audio.mp3"
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-vn",
            "-ar", "16000",
            "-ac", "1",
            "-q:a", "0",
            str(audio_path),
        ],
        check=True,
        capture_output=True,
    )
    return audio_path


def transcribe(audio_path: Path, model: str, language: str | None) -> str:
    try:
        import mlx_whisper
    except ImportError:
        sys.exit("mlx-whisper がインストールされていません。setup.sh を実行してください。")

    kwargs: dict = {"path_or_hf_repo": model}
    if language:
        kwargs["language"] = language

    result = mlx_whisper.transcribe(str(audio_path), **kwargs)
    return result["text"]


def main() -> None:
    parser = argparse.ArgumentParser(description="音声・動画ファイルをテキストに変換する")
    parser.add_argument("file", help="変換する音声または動画ファイルのパス")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Whisper モデル（HuggingFace repo ID）")
    parser.add_argument("--language", default=None, help="言語コード（例: ja, en）。省略で自動検出")
    args = parser.parse_args()

    input_path = Path(args.file)
    if not input_path.exists():
        sys.exit(f"ファイルが見つかりません: {input_path}")

    if input_path.suffix.lower() in VIDEO_EXTENSIONS:
        with tempfile.TemporaryDirectory() as tmp_dir:
            audio_path = extract_audio(input_path, tmp_dir)
            text = transcribe(audio_path, args.model, args.language)
    else:
        text = transcribe(input_path, args.model, args.language)

    print(text)


if __name__ == "__main__":
    main()
