import edge_tts
import asyncio
import shutil
import uuid
import os
import wave

OUTPUT_DIR = "generated_audio"
os.makedirs(OUTPUT_DIR, exist_ok=True)

VOICE_MAP = {
    # English
    "aria":      "en-US-AriaNeural",
    "atlas":     "en-GB-RyanNeural",
    "nova":      "en-AU-NatashaNeural",
    "echo":      "en-US-GuyNeural",
    "luna":      "en-US-JennyNeural",
    "rex":       "en-GB-LibbyNeural",
    "sage":      "en-CA-ClaraNeural",
    "orion":     "en-AU-WilliamNeural",
    "claire":    "en-US-MichelleNeural",
    "james":     "en-GB-ThomasNeural",
    # Hindi
    "hi_swara":  "hi-IN-SwaraNeural",
    "hi_madhur": "hi-IN-MadhurNeural",
    # Spanish
    "es_elvira": "es-ES-ElviraNeural",
    "es_alvaro": "es-ES-AlvaroNeural",
    # French
    "fr_denise": "fr-FR-DeniseNeural",
    "fr_henri":  "fr-FR-HenriNeural",
    # German
    "de_katja":  "de-DE-KatjaNeural",
    "de_konrad": "de-DE-ConradNeural",
    # Japanese
    "ja_nanami": "ja-JP-NanamiNeural",
    "ja_keita":  "ja-JP-KeitaNeural",
}

def speed_to_rate(speed: float) -> str:
    pct = int((speed - 1.0) * 100)
    return f"+{pct}%" if pct >= 0 else f"{pct}%"

def pitch_to_hz(pitch: int) -> str:
    hz = pitch * 5
    return f"+{hz}Hz" if hz >= 0 else f"{hz}Hz"

async def _generate(text: str, voice: str, rate: str, pitch: str, filepath: str):
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        pitch=pitch,
    )
    await communicate.save(filepath)

def mp3_to_wav(mp3_path: str, wav_path: str):
    """Convert MP3 to WAV. Uses ffmpeg (via pydub) when installed,
    otherwise PyAV, which is already installed with faster-whisper."""

    if shutil.which("ffmpeg"):
        from pydub import AudioSegment
        AudioSegment.from_mp3(mp3_path).export(wav_path, format="wav")
        return

    import av

    with av.open(mp3_path) as container:
        stream = container.streams.audio[0]
        rate = stream.rate or 24000
        resampler = av.AudioResampler(format="s16", layout="mono", rate=rate)

        with wave.open(wav_path, "wb") as out:
            out.setnchannels(1)
            out.setsampwidth(2)
            out.setframerate(rate)

            def write(frames):
                for frame in frames:
                    out.writeframes(bytes(frame.planes[0])[: frame.samples * 2])

            for frame in container.decode(stream):
                write(resampler.resample(frame))
            write(resampler.resample(None))


def text_to_speech(
    text: str,
    voice: str = "aria",
    speed: float = 1.0,
    pitch: int = 0,
    export_format: str = "mp3"
) -> str:
    uid = uuid.uuid4()
    voice_name = VOICE_MAP.get(voice.lower(), VOICE_MAP["aria"])
    rate = speed_to_rate(speed)
    pitch_str = pitch_to_hz(pitch)

    mp3_path = os.path.join(OUTPUT_DIR, f"audio_{uid}.mp3")
    asyncio.run(_generate(text, voice_name, rate, pitch_str, mp3_path))

    if export_format.lower() == "wav":
        wav_path = os.path.join(OUTPUT_DIR, f"audio_{uid}.wav")
        mp3_to_wav(mp3_path, wav_path)
        os.remove(mp3_path)
        return wav_path

    return mp3_path