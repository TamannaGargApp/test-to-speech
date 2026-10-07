from docx import Document


def read_file(filepath: str) -> str:
    """
    Read text content from .txt or .docx files.
    """

    if filepath.endswith(".txt"):
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read()

    if filepath.endswith(".docx"):
        document = Document(filepath)

        return "\n".join(paragraph.text for paragraph in document.paragraphs)

    raise ValueError("Unsupported file type. Only .txt and .docx files are allowed.")
