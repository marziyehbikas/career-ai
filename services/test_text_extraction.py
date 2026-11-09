from pathlib import Path

from resume_text_extractor import extract_resume_text


file_path = Path(
    r"D:\Projects\career-ai-backend\uploads\resumes\c3f9ef48-9688-4e41-a8e4-f81c309fd7d9.docx"
)

text = extract_resume_text(file_path)

print("Extracted text:")
print(text[:2000])

print("\nTotal characters:", len(text))

if not text:
    print(
        "No selectable text was extracted. "
        "The PDF might be scanned."
    )