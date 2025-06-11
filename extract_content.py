import os
import glob
import markdown
from bs4 import BeautifulSoup

def md_to_text(md_content):
    html = markdown.markdown(md_content)
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()

def collect_course_text(base_folder="./tds-content"):
    all_text = []
    md_files = glob.glob(os.path.join(base_folder, "**/*.md"), recursive=True)

    for file_path in md_files:
        with open(file_path, "r", encoding="utf-8") as f:
            md_content = f.read()
            text = md_to_text(md_content)
            all_text.append(f"\n--- {file_path} ---\n")
            all_text.append(text)

    return "\n".join(all_text)

if __name__ == "__main__":
    full_text = collect_course_text()
    with open("course_context.txt", "w", encoding="utf-8") as out:
        out.write(full_text)
    print("✅ Course content saved to course_context.txt")

