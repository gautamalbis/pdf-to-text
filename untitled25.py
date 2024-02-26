import os
import pdfplumber
import pytesseract
import io
import magic
from PIL import Image

def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        data = []
        for page_number, page in enumerate(pdf.pages):
            text = page.extract_text()
            images = page.images

            for img_index, img_data in enumerate(images):
                try:
                    img_bytes = img_data['stream'].get_data()
                    #print(img_data)

                    image_format = magic.from_buffer(img_bytes, mime=True)

                    image_filename = f"image_{page_number}_{img_index}.{image_format.split('/')[-1]}"
                    with open(image_filename, "wb") as f:
                        f.write(img_bytes)

                    img = Image.open(image_filename).convert("RGB")
                    pytesseract.pytesseract.tesseract_cmd =r'C:\Program Files\Tesseract-OCR\tesseract.exe'

                    img_text = pytesseract.image_to_string(img)

                    if img_text is not None:
                        data.append({
                            "page_number": page_number,
                            "text": text,
                            "image_text": img_text,
                        })

                except Exception as e:
                    print(f"Error extracting text from image {img_index}: {e}")

        return data

if __name__ == "__main__":
    pdf_path = "pp.pdf"
    extracted_data = extract_text_from_pdf(pdf_path)
    print(extracted_data)