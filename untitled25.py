import os
import pdfplumber
import io
import magic
from PIL import Image
import subprocess
import cv2

'''image = cv2.imread("image.jpg")
grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
ret, thresh_image = cv2.threshold(grayscale_image, 127, 255, cv2.THRESH_BINARY)
cv2.imwrite("processed_image.png", thresh_image)
 height, width, _ = image.shape 
    estimated_dpi = (desired_dpi * 25.4) / max(height, width) 
    new_width, new_height = (int(width * desired_dpi / estimated_dpi), int(height * desired_dpi / estimated_dpi))

    if estimated_dpi < desired_dpi:
        pil_image = Image.open(image_path)
        resized_image = pil_image.resize((new_width, new_height), Image.ANTIALIAS)
        resized_image.save("resized_" + image_path)
        print(f"Image resized to approximately {estimated_dpi:.2f} DPI.")
    else:
        print(f"Image DPI is already at least {estimated_dpi:.2f} (estimated).")'''

def extract_image_text(image_filename):
    output=image_filename
    print("yes")
    tesseract_cmd=f"tesseract {image_filename}.png {output}"
    try:
        subprocess.run(tesseract_cmd,shell=True,check=True,stderr=subprocess.DEVNULL)
        print("Ocr was completed")

        with open(f'{output}.txt','r') as file:
            text_data=file.read()
            return text_data
    except subprocess.CalledProcessError as e:
        print(f'Ocr failed error: {e}')

def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        data = []
        text=''
        for page_number, page in enumerate(pdf.pages):
            text += page.extract_text()
            images = page.images

            for img_index, img_data in enumerate(images):
                try:
                    img_bytes = img_data['stream'].get_data()
                    #print(img_data)

                    image_format = magic.from_buffer(img_bytes, mime=True)

                    image_filename = f"image_{page_number}_{img_index}.{image_format.split('/')[-1]}"
                    with open(image_filename, "wb") as f:
                        f.write(img_bytes)
                    
                    img=Image.open(image_filename).convert('RGB')
                    image_filename=image_filename.split('.')[0]
                    img.save(f'{image_filename}.png')
                    
            
                    print(image_filename)
                    tt=extract_image_text(image_filename)

                    text+=tt

                except Exception as e:
                    pass
                    #print(f"Error extracting text from image {img_index}: {e}")
        directory='.'
        prefix="image"
        allfiles=os.listdir(directory)
        match_file=[file for file in allfiles if file.startswith(prefix)]
        for ff in match_file:
            file_path=os.path.join(directory,ff)
            os.remove(file_path)


        return text

if __name__ == "__main__":
    pdf_path = "machine_article.pdf"
    extracted_data = extract_text_from_pdf(pdf_path)
    
    print(extracted_data)
