---
name: audio-transcription
description: 音声・動画ファイルをテキストに変換する（mlx-whisper / Apple Silicon 専用）
version: 1.0.0
command-dispatch: "tool"
command-tool: exec
command-arg-mode: raw
user-invocable: true
metadata: {"openclaw": {"requires": {"bins": ["python3", "ffmpeg"]}, "os": ["macos"], "install": [{"kind": "brew", "formula": "ffmpeg"}]}}
---

## 使い方

```
/audio-transcription <ファイルパス> [オプション]
```

音声・動画ファイルをテキストに変換して stdout に出力します。

## 対応フォーマット

- 音声: `.mp3` `.wav` `.m4a` `.flac` `.ogg` `.aac`
- 動画: `.mp4` `.mov` `.mkv` `.avi` `.webm`（ffmpeg で音声を自動抽出）

## オプション

| 引数 | 説明 | デフォルト |
|------|------|-----------|
| `--model` | Whisper モデル（HuggingFace repo ID） | `mlx-community/whisper-large-v3-turbo` |
| `--language` | 言語コード（例: `ja` `en`）。省略で自動検出 | 自動 |

## 例

```sh
/audio-transcription /path/to/audio.mp3
/audio-transcription /path/to/video.mp4 --language ja
/audio-transcription /path/to/audio.wav --model mlx-community/whisper-base
```

## セットアップ

```sh
./setup.sh
```

## 呼び出し元からの利用

```python
import os, subprocess

SKILL_DIR = os.environ.get("AUDIO_TRANSCRIPTION_SKILL_DIR", "/path/to/skill-audio-transcription")

result = subprocess.run(
    ["python3", f"{SKILL_DIR}/transcribe.py", audio_path],
    capture_output=True, text=True, check=True
)
transcript = result.stdout.strip()
```
