import os
import json
import base64
from pathlib import Path
from mistralai.models import OCRResponse
from mistralai import Mistral, DocumentURLChunk

def processDoc(uploads_dir, file_name, intermediatory_dir, MISTRAL_API_KEY):
    doc_path = os.path.join(uploads_dir, file_name)
    document = Path(doc_path)
    assert document.is_file()

    MISTRAL_CLIENT = Mistral(api_key=MISTRAL_API_KEY)

    uploaded_doc = MISTRAL_CLIENT.files.upload(
        file={
            "file_name": document.stem,
            "content": document.read_bytes(),
        },
        purpose="ocr",
    )

    signed_url = MISTRAL_CLIENT.files.get_signed_url(file_id=uploaded_doc.id, expiry=1)

    ocr_response = MISTRAL_CLIENT.ocr.process(
        document=DocumentURLChunk(document_url=signed_url.url),
        model="mistral-ocr-latest",
        include_image_base64=True
    )

    saveData(ocr_response, file_name, intermediatory_dir)

def saveData(ocr_response, file_name, intermediatory_dir):
    page_data = {}

    for page in ocr_response.pages:
        image_names = []

        for img in page.images:
            image_file_path = os.path.join(intermediatory_dir, img.id)
            _ , encoded = img.image_base64.split(",", 1)
            image_data = base64.b64decode(encoded)

            with open(image_file_path, "wb") as img_file:
                img_file.write(image_data)

            image_names.append(img.id)

        page_data[page.index] = [page.markdown, image_names]

    _, extension = os.path.splitext(file_name)
    extension = extension.lower()

    json_file_name = file_name.replace(extension, ".json")
    json_file_path = os.path.join(intermediatory_dir, json_file_name)
    
    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(page_data, json_file, indent=4)

