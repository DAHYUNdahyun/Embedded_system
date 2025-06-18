from PIL import Image
import os  # ✅ 꼭 필요

folder = "assets/"

for filename in os.listdir(folder):
    if filename.endswith(".png") and "tama" in filename:
        path = os.path.join(folder, filename)
        img = Image.open(path)
        cropped = img.crop(img.getbbox())
        cropped.save(path)  # 원본 덮어쓰기
        print(f"✅ {filename} 여백 제거 완료")
