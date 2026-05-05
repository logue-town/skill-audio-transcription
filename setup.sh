#!/usr/bin/env bash
set -euo pipefail

echo "=== audio-transcription setup ==="

# python3
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 が見つかりません。Homebrew または公式サイトからインストールしてください。"
    exit 1
fi

# ffmpeg
if ! command -v ffmpeg &>/dev/null; then
    echo "ffmpeg が見つかりません。Homebrew でインストールします..."
    brew install ffmpeg
fi

# mlx-whisper
echo "mlx-whisper をインストール（または更新）します..."
pip3 install --upgrade mlx-whisper

echo ""
echo "セットアップ完了。動作確認:"
echo "  python3 transcribe.py /path/to/audio.mp3"
