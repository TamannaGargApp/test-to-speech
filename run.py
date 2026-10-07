from gtts import gTTS
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from docx import Document
import tempfile
import time

root = tk.Tk()
root.title("Text to Speech")
canvas = tk.Canvas(root, width=400, height=300)
canvas.pack()

entry = tk.Entry(root, width=40)
canvas.create_window(200, 120, window=entry)

entry.delete(0, tk.END)


def split_text(text, max_chars=4000):
    # Splits text into chunks that don't exceed max_chars, trying to split on sentence boundaries
    chunks = []
    while len(text) > max_chars:
        split_at = text.rfind(".", 0, max_chars)
        if split_at == -1:
            split_at = max_chars
        chunks.append(text[: split_at + 1])
        text = text[split_at + 1 :]
    chunks.append(text)
    return chunks


def texttospeech():
    text = entry.get()
    if not text.strip():
        messagebox.showwarning(
            "Input Error", "Please enter some text or select a file."
        )
        return

    chunks = split_text(text)
    temp_dir = tempfile.mkdtemp()
    audio_files = []

    try:
        for i, chunk in enumerate(chunks):
            tts = gTTS(text=chunk, lang="en", slow=False)
            filename = os.path.join(temp_dir, f"chunk_{i}.mp3")
            tts.save(filename)
            audio_files.append(filename)

        # Play all chunks in order
        for audio in audio_files:
            os.system(
                f"start {audio}"
            )  # Replace 'start' with 'open' on macOS or 'xdg-open' on Linux
            time.sleep(2)  # Small delay to let audio start (adjust as needed)

    except Exception as e:
        messagebox.showerror("Speech Error", f"An error occurred:\n{e}")


def browsefile():
    filepath = filedialog.askopenfilename(
        filetypes=[("Text and Word files", "*.txt *.docx")],
        title="Select a text or DOCX file",
    )
    if filepath:
        try:
            content = ""
            if filepath.endswith(".txt"):
                with open(filepath, "r", encoding="utf-8") as file:
                    content = file.read()
            elif filepath.endswith(".docx"):
                doc = Document(filepath)
                content = "\n".join([para.text for para in doc.paragraphs])
            else:
                messagebox.showerror(
                    "Unsupported File", "Please select a .txt or .docx file only."
                )
                return

            entry.delete(0, tk.END)
            entry.insert(0, content[:500])  # Preview only
            entry.full_text = content  # Save full content for TTS
        except Exception as e:
            messagebox.showerror("File Error", f"Could not read file:\n{e}")


# Use full content from file if available
def safe_text_get():
    return getattr(entry, "full_text", entry.get())


# Override texttospeech to get full content from file
def texttospeech_with_file_support():
    entry_text = safe_text_get()
    entry.delete(0, tk.END)  # Optional: clear UI
    entry.insert(0, entry_text[:500])  # Preview
    texttospeech()


# Convert button
button = tk.Button(
    text="Convert Text to Speech", command=texttospeech_with_file_support
)
canvas.create_window(280, 180, window=button)

# File browse button
browse_button = tk.Button(text="Browse File (.txt / .docx)", command=browsefile)
canvas.create_window(120, 180, window=browse_button)

root.mainloop()
