# skill-audio-transcription

音声・動画ファイルをテキストに変換する [OpenClaw](https://openclaw.dev) スキル。  
Apple Silicon の MLX を使った [mlx-whisper](https://github.com/ml-explore/mlx-examples/tree/main/whisper) により、標準 Whisper より高速に文字起こしを行います。

![platform](https://img.shields.io/badge/platform-macOS%20Apple%20Silicon-ffffff?logo=apple&labelColor=555555)
![python](https://img.shields.io/badge/python-3.10%2B-ffffff?logo=python&labelColor=555555)
![ffmpeg](https://img.shields.io/badge/requires-ffmpeg-ffffff?labelColor=555555)

---

## インストール

```sh
# OpenClaw 経由（推奨）
openclaw skills install audio-transcription

# または手動
git clone https://github.com/logue-town/skill-audio-transcription
cd skill-audio-transcription
./setup.sh
```

`setup.sh` は `mlx-whisper` の pip インストールと ffmpeg の有無チェックを行います。  
ffmpeg が未インストールの場合は `brew install ffmpeg` で導入してください。

## 使い方

### OpenClaw スキルとして

```
/audio-transcription /path/to/audio.mp3
/audio-transcription /path/to/video.mp4 --language ja
```

### コマンドラインから直接

```sh
python3 transcribe.py /path/to/audio.mp3
python3 transcribe.py /path/to/video.mp4 --language ja --model mlx-community/whisper-base
```

### 他スクリプトから呼ぶ

```python
import os, subprocess

SKILL_DIR = os.environ.get("AUDIO_TRANSCRIPTION_SKILL_DIR", "/path/to/skill-audio-transcription")

result = subprocess.run(
    ["python3", f"{SKILL_DIR}/transcribe.py", audio_path],
    capture_output=True, text=True, check=True,
)
transcript = result.stdout.strip()
```

## オプション

| 引数 | 説明 | デフォルト |
|------|------|-----------|
| `--model` | Whisper モデル（HuggingFace repo ID） | `mlx-community/whisper-large-v3-turbo` |
| `--language` | 言語コード（例: `ja`, `en`）。省略で自動検出 | 自動 |

## 対応フォーマット

- 音声: `.mp3` `.wav` `.m4a` `.flac` `.ogg` `.aac`
- 動画: `.mp4` `.mov` `.mkv` `.avi` `.webm`（内部で ffmpeg が音声を自動抽出）

## テスト

```sh
uv run pytest tests/ -v
```

ffmpeg が未インストールの場合、動画抽出まわりの 4 テストはスキップされます。

## ライセンス

MIT-0