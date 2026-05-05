"""transcribe.py のテスト。mlx-whisper はモック、ffmpeg は実際に使用する。"""

import math
import shutil
import struct
import subprocess
import sys
import wave
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import transcribe

# ---------------------------------------------------------------------------
# Helpers / markers
# ---------------------------------------------------------------------------

requires_ffmpeg = pytest.mark.skipif(
    shutil.which("ffmpeg") is None,
    reason="ffmpeg がインストールされていません",
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_mlx():
    """mlx_whisper モジュールのモック。sys.modules 経由でレイジーインポートを差し替える。"""
    mock = MagicMock()
    mock.transcribe.return_value = {"text": "こんにちは世界"}
    with patch.dict(sys.modules, {"mlx_whisper": mock}):
        yield mock


@pytest.fixture
def audio_file(tmp_path):
    """Python wave モジュールで生成した 0.1 秒サイン波 .wav（ffmpeg 不要）。"""
    path = tmp_path / "test.wav"
    sample_rate = 16000
    num_samples = int(sample_rate * 0.1)
    samples = [
        int(32767 * math.sin(2 * math.pi * 440 * i / sample_rate))
        for i in range(num_samples)
    ]
    with wave.open(str(path), "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(struct.pack(f"<{num_samples}h", *samples))
    return path


@pytest.fixture
def video_file(tmp_path):
    """ffmpeg lavfi で生成した 1 秒テスト動画 .mp4（映像＋サイン波）。"""
    if shutil.which("ffmpeg") is None:
        pytest.skip("ffmpeg がインストールされていません")
    path = tmp_path / "test.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "testsrc=duration=1:size=64x64:rate=1",
            "-f", "lavfi", "-i", "sine=frequency=440:duration=1",
            "-shortest", str(path),
        ],
        check=True,
        capture_output=True,
    )
    return path


# ---------------------------------------------------------------------------
# extract_audio
# ---------------------------------------------------------------------------


@requires_ffmpeg
def test_extract_audio_creates_mp3(video_file, tmp_path):
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    result = transcribe.extract_audio(video_file, str(out_dir))
    assert result.exists()
    assert result.suffix == ".mp3"


@requires_ffmpeg
def test_extract_audio_output_path(video_file, tmp_path):
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    result = transcribe.extract_audio(video_file, str(out_dir))
    assert result == out_dir / "audio.mp3"


@requires_ffmpeg
def test_extract_audio_invalid_file_raises(tmp_path):
    with pytest.raises(subprocess.CalledProcessError):
        transcribe.extract_audio(tmp_path / "nonexistent.mp4", str(tmp_path))


# ---------------------------------------------------------------------------
# transcribe()
# ---------------------------------------------------------------------------


def test_transcribe_returns_text(audio_file, mock_mlx):
    result = transcribe.transcribe(audio_file, transcribe.DEFAULT_MODEL, None)
    assert result == "こんにちは世界"


def test_transcribe_default_model(audio_file, mock_mlx):
    transcribe.transcribe(audio_file, transcribe.DEFAULT_MODEL, None)
    mock_mlx.transcribe.assert_called_once_with(
        str(audio_file), path_or_hf_repo=transcribe.DEFAULT_MODEL
    )


def test_transcribe_custom_model(audio_file, mock_mlx):
    custom = "mlx-community/whisper-base"
    transcribe.transcribe(audio_file, custom, None)
    mock_mlx.transcribe.assert_called_once_with(
        str(audio_file), path_or_hf_repo=custom
    )


def test_transcribe_no_language_kwarg_when_none(audio_file, mock_mlx):
    transcribe.transcribe(audio_file, transcribe.DEFAULT_MODEL, None)
    kwargs = mock_mlx.transcribe.call_args.kwargs
    assert "language" not in kwargs


def test_transcribe_passes_language(audio_file, mock_mlx):
    transcribe.transcribe(audio_file, transcribe.DEFAULT_MODEL, "ja")
    kwargs = mock_mlx.transcribe.call_args.kwargs
    assert kwargs.get("language") == "ja"


def test_transcribe_missing_mlx_whisper_exits(audio_file):
    # sys.modules に None をセットすると import 時に ImportError が発生する
    with patch.dict(sys.modules, {"mlx_whisper": None}):
        with pytest.raises(SystemExit):
            transcribe.transcribe(audio_file, transcribe.DEFAULT_MODEL, None)


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------


def test_main_audio_file(audio_file, mock_mlx, capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["transcribe.py", str(audio_file)])
    transcribe.main()
    assert capsys.readouterr().out.strip() == "こんにちは世界"


@requires_ffmpeg
def test_main_video_file(video_file, mock_mlx, capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["transcribe.py", str(video_file)])
    transcribe.main()
    assert capsys.readouterr().out.strip() == "こんにちは世界"


def test_main_file_not_found(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["transcribe.py", "/nonexistent/file.mp3"])
    with pytest.raises(SystemExit) as exc:
        transcribe.main()
    assert exc.value.code  # 空でない文字列 = エラー終了


def test_main_custom_model_arg(audio_file, mock_mlx, monkeypatch):
    monkeypatch.setattr(
        sys, "argv",
        ["transcribe.py", str(audio_file), "--model", "mlx-community/whisper-base"],
    )
    transcribe.main()
    assert (
        mock_mlx.transcribe.call_args.kwargs["path_or_hf_repo"]
        == "mlx-community/whisper-base"
    )


def test_main_language_arg(audio_file, mock_mlx, monkeypatch):
    monkeypatch.setattr(
        sys, "argv",
        ["transcribe.py", str(audio_file), "--language", "ja"],
    )
    transcribe.main()
    assert mock_mlx.transcribe.call_args.kwargs.get("language") == "ja"
