from pathlib import Path

import pymupdf
from docx import Document


def extract_resume_text(file_path: str | Path) -> str:
    # 1. Convert the provided path into a Path object.
    path = Path(file_path)

    # 2. Check whether the file exists.
    if not path.is_file():
        raise FileNotFoundError(
            f"Resume file not found: {path}"
        )

    # 3. Identify the file type using its extension.
    extension = path.suffix.lower()

    # 4. Extract text from a PDF.
    if extension == ".pdf":
        with pymupdf.open(path) as pdf: # opens the existing PDF document so Python can read its contents
            # List comprehension
            # Its syntax: [expression for item in iterable]
            # What it does: For each page in pdf, get that page's text and put it into a list called pages_text
            pages_text = [
                page.get_text("text") # ("text") is the format of the text 
                for page in pdf
            ]

        text = "\n".join(pages_text) # Combines the extracted page text into one string, separating pages with newline characters.

    # 5. Extract text from a DOCX file.
    elif extension == ".docx":
        document = Document(str(path))
                  # Document opens the existing Word document so we can read its contents.

        text_parts = []

        # Extract ordinary paragraphs.
        # document.paragraphs gives us the document's ordinary paragraphs
        for paragraph in document.paragraphs:
            if paragraph.text.strip(): # checks whether the paragraph contains any actual text after removing whitespace from the beginning and end.
                text_parts.append(paragraph.text.strip())

        # Extract text inside tables.
        for table in document.tables:
            for row in table.rows:
                cells = [
                    cell.text.strip()
                    for cell in row.cells
                ]

                if any(cells):
                    text_parts.append(" | ".join(cells))
                    # Adds the extracted cells text into one string, separating cells with | characters.
                    # Original cells => cells = ["BSc", "University A", "2021"]
                    # Added to text_parts => BSc | University A | 2021


        text = "\n".join(text_parts)
        # he join() method combines everything into one string, placing a newline between each item

    # 6. Reject unsupported file types.
    else:
        raise ValueError(
            "Only PDF and DOCX files are supported."
        )

    # 7. Return the extracted text.
    return text.strip()