from PIL import Image
import os

folder = "assets/game/"

for filename in os.listdir(folder):
    if filename.endswith(".png"):
        path = os.path.join(folder, filename)
        img = Image.open(path)
        cropped = img.crop(img.getbbox())  # 투명 여백 제거
        cropped.save(path)  # 덮어쓰기
        print(f"✅ {filename} 여백 제거 완료")
