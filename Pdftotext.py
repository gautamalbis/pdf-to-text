import os
import pdfplumber
import io
import magic
from PIL import Image
import subprocess
from io import StringIO
import cv2




def extract_image_text(image_filename):
    output=image_filename.split(".")[0]
    print("yes")
    tesseract_cmd=f"tesseract {image_filename} {output} --psm 6"
    try:
        subprocess.run(tesseract_cmd,shell=True,check=True,stderr=subprocess.DEVNULL)
        print("Ocr was completed")

        with open(f'{output}.txt','r') as file:
            text_data=file.read()
            return text_data
    except subprocess.CalledProcessError as e:
        print(f'Ocr failed error: {e}')

def resize_image(image_path,target_dpi=300):
  print(image_path,"resize_image")
  image = Image.open(f'{image_path}.png')
  print(image.size)
  ori_dpi = max(image.info.get('dpi', (72, 72)))
  factor = min(target_dpi / ori_dpi, 2)

  new_width = int(image.width * factor)
  new_height = int(image.height * factor)
  resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
  print(resized_image.size)
  resized_image.save(f"{image_path}_pp.png")
  image = cv2.imread(f"{image_path}_pp.png")
  #print(image)
  grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  ret, thresh_image = cv2.threshold(grayscale_image, 127, 255, cv2.THRESH_BINARY)
  print(thresh_image)
  cv2.imwrite(f"{image_path}_processed.png", thresh_image)
  print("done")
  cv2.destroyAllWindows()
  return f"{image_path}_pp.png"

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
                    if image_filename.split(".")[-1]=="octet-stream":
                        img=Image.open(StringIO.StringIo(image_filename))
                        print(img.size,"octet")
                    else:
                        img=Image.open(image_filename).convert('RGB')
                    desired_dpi=300
                    image_filename=image_filename.split('.')[0]
                    img.save(f'{image_filename}.png')
                    #pre processing
                    pre_process=resize_image(image_filename,desired_dpi)


                    print(image_filename)
                    tt=extract_image_text(pre_process)

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
    pdf_path = "papers.pdf"
    extracted_data = extract_text_from_pdf(pdf_path)

    print(extracted_data)