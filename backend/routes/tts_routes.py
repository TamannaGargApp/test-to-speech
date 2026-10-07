from gtts import gTTS
import uuid
import os


OUTPUT_DIR = "generated_audio"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


def text_to_speech(text: str):

    filename = (
        f"audio_{uuid.uuid4()}.mp3"
    )

    filepath = os.path.join(
        OUTPUT_DIR,
        filename
    )

    tts = gTTS(
        text=text,
        lang="en",
        slow=False
    )

    tts.save(filepath)

    return filepath