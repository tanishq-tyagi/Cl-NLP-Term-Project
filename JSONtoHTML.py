import os
import json
import google.generativeai as genai
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

from cleanupcrew import generateRandomSuffix

def JSONtoHTML(intermediatory_dir, output_dir, GEMINI_API_KEY):
    combined_list = []
    files =  [f for f in os.listdir(intermediatory_dir) if os.path.isfile(os.path.join(intermediatory_dir, f))]

    for file in files:
        _, extension = os.path.splitext(file)
        extension = extension.lower()

        if (extension == ".json"):
            file_path = os.path.join(intermediatory_dir, file)

            with open(file_path, 'r') as json_file:
                data = json.load(json_file)
                for key in data:
                    combined_list.append(data[key])

    base_prompt = """

        You are a superior tutor specializing in creating study materials for exams.

        Input: A list of sections. Each section is of the form:
        [
            "markdown_text_from_OCR",
            ["optional_image_path"]
        ]

        - The first element is OCR-detected markdown text from scanned academic documents.
        - The second element may contain an image path to an image relevant to that text. If present, you must include the image in the correct spot using <img src="path" /> HTML tag.

        Task:
        - Parse and deeply understand the provided markdown content.
        - If there are gaps, missing explanations, incomplete points, or missing context, intelligently complete the material as a human expert tutor would. (You may add examples, clarifications, or brief context expansions if needed.)
        - Transform the entire information into a clean, structured HTML format.
        - ONLY generate the contents inside a single <body> tag. Do NOT add CSS, <head>, <html>, or any styling.
        - The structure must prioritize exam study efficiency. Use clear headings (<h1>, <h2>, <h3>), paragraphs (<p>), bullet points (<ul><li>), numbered lists (<ol><li>), etc.
        - Insert <img src="path" /> whenever an image path is provided in the second element of the section.

        Constraints:
        - Be highly organized, logical, and focus on educational clarity.
        - Prefer small sections with clear headers over long paragraphs.
        - Keep everything concise but complete — no fluff.
        - Assume the reader is studying for an exam and needs to quickly absorb and revise the key points.
        - Stay faithful to the original OCR text unless improving missing parts.

        Output:
        Only the <body> tag content, clean and complete.

        Now begin.


        """
    
    final_prompt = base_prompt + str(combined_list)

    genai.configure(api_key=GEMINI_API_KEY)
    GEMINI_MODEL = genai.GenerativeModel("gemini-1.5-flash")

    html_response = GEMINI_MODEL.generate_content(final_prompt)

    html_content = html_response.text
    full_html = f'<html><body>\n{html_content}\n</body></html>'

    if ("```html" in full_html and "```" in full_html):
        clean_html = full_html.replace("```html", "")
        clean_html = clean_html.replace("```", "")

    elif ("```html" in full_html):
        clean_html = full_html.replace("```html", "")
        
    elif ("```" in full_html):
        clean_html = full_html.replace("```", "")

    # html_file_path = os.path.join(output_dir, "output.html")
    # with open(html_file_path, "w", encoding="utf-8") as html_file:
    #     html_file.write(clean_html)

    n = generateRandomSuffix()
    output_pdf_path = os.path.join(output_dir, f"output{n}.pdf")

    with open("main.css", "r") as css_file:
        css_content = css_file.read()


    font_config = FontConfiguration()
    html = HTML(string=clean_html, base_url=os.getcwd()+intermediatory_dir)
    css = CSS(string=css_content, font_config=font_config)
    html.write_pdf(
        output_pdf_path, stylesheets=[css],
        font_config=font_config)