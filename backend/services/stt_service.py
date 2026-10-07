import os
import threading

from faster_whisper import WhisperModel

# Model size: tiny, base, small, medium, large-v3 (bigger = more accurate, slower).
# The model is downloaded automatically the first time it is used.
STT_MODEL = os.getenv("STT_MODEL", "base")

_model = None
_model_lock = threading.Lock()


def _get_model() -> WhisperModel:
    global _model

    with _model_lock:
        if _model is None:
            _model = WhisperModel(
                STT_MODEL,
                device="cpu",
                compute_type="int8"
            )

    return _model


def speech_to_text(audio_path: str, language: str = None) -> dict:
    """
    Transcribe an audio file (mp3, wav, webm, ogg, m4a, ...) to text.
    language: ISO code such as "en" or "hi", or None to auto-detect.
    """

    segments, info = _get_model().transcribe(
        audio_path,
        language=language or None,
        vad_filter=True
    )

    text = " ".join(segment.text.strip() for segment in segments).strip()

    return {
        "text": text,
        "language": info.language,
        "duration": round(info.duration, 1)
    }
