import os

from cleanupcrew import createInitialDirs, janitor
from docs_processing import processDoc
from image_processing import processImage
from JSONtoHTML import JSONtoHTML
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.local")

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def main():
    uploads_dir = ".\\uploads"
    intermediatory_dir = ".\\intermediate"
    output_dir = ".\\output"

    required_dirs = [intermediatory_dir, output_dir, uploads_dir]
    createInitialDirs(required_dirs)

    files = [f for f in os.listdir(uploads_dir) if os.path.isfile(os.path.join(uploads_dir, f))]

    for file in files:
        _, extension = os.path.splitext(file)
        extension = extension.lower()
        if (extension == ".pdf" or extension == ".docx" or extension == ".ppt"):
            processDoc(uploads_dir, file, intermediatory_dir, MISTRAL_API_KEY)

        elif(extension == ".png" or extension == ".jpg" or extension == ".jpeg"):
            processImage(uploads_dir, file, intermediatory_dir, GEMINI_API_KEY)

        else:
            print(f"The following file has unsupported type: {file}")

    JSONtoHTML(intermediatory_dir, output_dir, GEMINI_API_KEY)

    janitor(intermediatory_dir)

    janitor(uploads_dir)

if __name__ == '__main__':
    main()