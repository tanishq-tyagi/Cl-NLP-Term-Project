import os
import io
import json
import shutil
from PIL import Image
import google.generativeai as genai

def processImage(uploads_dir, file_name, intermediatory_dir, GEMINI_API_KEY):
    genai.configure(api_key=GEMINI_API_KEY)
    GEMINI_MODEL = genai.GenerativeModel("gemini-1.5-flash")

    image_path = os.path.join(uploads_dir, file_name)

    copied_image_path = os.path.join(intermediatory_dir, file_name)
    shutil.copy2(image_path, copied_image_path)

    image = Image.open(image_path)
        
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=image.format if image.format else 'PNG')
    img_byte_arr = img_byte_arr.getvalue()

    title_gen_prompt = "You are among the world's best descriptor. Analyze the given image. And then create a title for this image. Give one title only. No fancy editing just plain text. No \n at end."

    title = GEMINI_MODEL.generate_content([
        title_gen_prompt,
        {"mime_type": f"image/{image.format.lower() if image.format else 'png'}", 
            "data": img_byte_arr}
    ])

    title = title.text
    if title.endswith('\n'):
        title = title.rstrip('\n')

    markdown_title = f"# **{title}**\n\n![{file_name}]({file_name})\n\n"

    json_dict = {}
    json_dict["0"] = [markdown_title, [file_name]]

    _, extension = os.path.splitext(file_name)
    extension = extension.lower()

    json_file_name = file_name.replace(extension, ".json")
    json_file_path = os.path.join(intermediatory_dir, json_file_name)
    
    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(json_dict, json_file, indent=4)