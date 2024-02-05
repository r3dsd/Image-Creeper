from PIL import Image

def png_to_ico(png_path: str, ico_path: str):
    img = Image.open(png_path)
    # 이미지를 RGBA 모드로 변환 (투명도를 위해)
    img = img.convert("RGBA")
    if "icc_profile" in img.info:
        print("ICC 프로필 제거")
        del img.info["icc_profile"]
    img.save(ico_path, format='ICO')

def remove_icc_profile(png_path: str, save_path: str):
    img = Image.open(png_path)
    if "icc_profile" in img.info:
        print("ICC 프로필 제거")
        del img.info["icc_profile"]
    img.save(save_path)

remove_icc_profile("Icon.png", "Icon_no_icc.png")
png_to_ico("Icon_no_icc.png", "Icon.ico")

