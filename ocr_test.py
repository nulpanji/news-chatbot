from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from pyzbar.pyzbar import decode
import os
import pandas as pd
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

def extract_info_with_ocr_and_qr(pdf_path, poppler_path):
    images = convert_from_path(pdf_path, poppler_path=poppler_path)
    results = []
    crop_dir = 'company_crops'
    if not os.path.exists(crop_dir):
        os.makedirs(crop_dir)
    for i, img in enumerate(images):
        width, height = img.size
        crop_box = (100, 180, width-100, 700)  # 기업명+QR코드만 포함
        cropped_img = img.crop(crop_box)
        # OCR로 기업명 추출
        company_name = pytesseract.image_to_string(cropped_img, lang='kor').strip()
        # QR코드 추출
        qr_url = None
        decoded_objs = decode(cropped_img)
        for obj in decoded_objs:
            qr_url = obj.data.decode('utf-8')
            break
        crop_path = os.path.join(crop_dir, f'company_crop_page_{i+1}.png')
        cropped_img.save(crop_path)
        print(f"PDF {i+1} OCR 기업명: {company_name}")
        print(f"PDF {i+1} QR코드 URL: {qr_url}")
        results.append({'PDF_페이지': i+1, '기업명_OCR': company_name, 'QR코드_URL': qr_url})
    # 결과를 엑셀로 저장
    df = pd.DataFrame(results)
    df.to_excel('ocr_qr_results.xlsx', index=False)
    print(df)
    return results

if __name__ == "__main__":
    pdf_path = "sample.pdf"
    poppler_path = r"C:\\poppler\\Library\\bin"
    extract_info_with_ocr_and_qr(pdf_path, poppler_path)
