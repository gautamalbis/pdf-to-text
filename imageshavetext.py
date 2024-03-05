import os
import pdfplumber
import io
import magic
from PIL import Image
import subprocess
from io import StringIO
import cv2
import fitz


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
  image = Image.open(image_path)
  print(image.size)
  ori_dpi = max(image.info.get('dpi', (72, 72)))
  factor = min(target_dpi / ori_dpi, 2)

  new_width = int(image.width * factor)
  new_height = int(image.height * factor)
  resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
  print(resized_image.size)
  resized_image.save(image_path)
  '''image = cv2.imread(image_path)
  #print(image)
  grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  ret, thresh_image = cv2.threshold(grayscale_image, 127, 255, cv2.THRESH_BINARY)
  print(thresh_image)
  cv2.imwrite(image_path, thresh_image)
  print("done")
  cv2.destroyAllWindows()'''
  return image_path


def remove_allImages(directory):
    prefix="page"
    allfiles=os.listdir(directory)
    match_file=[file for file in allfiles if file.startswith(prefix)]
    for ff in match_file:
        file_path=os.path.join(directory,ff)
        os.remove(file_path)


def extract_image_from_pdf(doc,page_num,image_list):
    text_image=[]
    empty_data=[]
    for img_index, img_info in enumerate(image_list):
        img_index += 1
        print(img_info[0])
        img = fitz.Pixmap(doc, img_info[0])
        output_folder=directory
        img_file_path = f"{output_folder}/page{page_num + 1}_img{img_index}.png"
        img.save(img_file_path)
        pre_process=resize_image(img_file_path,300)
        tt=extract_image_text(pre_process)
        if tt:
            text_image.append(tt)
        else:
            empty_data.append(img_file_path)
    return text_image,empty_data   


def extract_text_from_pdf(pdf_path,directory):
    doc = fitz.open(pdf_path)
    text=""
    for page_num in range(doc.page_count):
        page = doc[page_num]
        text += page.get_text()
        image_list = page.get_images(full=True)
        textlist,emptylist=extract_image_from_pdf(doc,page_num,image_list)
        text+=textlist
        print(emptylist)

                    
    ##remove all images from directory
    remove_allImages(directory)

    doc.close()
    return text

if __name__ == "__main__":
    pdf_path = "pp.pdf"
    directory = 'output_folder'
    if not os.path.exists(directory):
        os.makedirs(directory)
    extracted_data = extract_text_from_pdf(pdf_path,directory)

    print(extracted_data)