import os
import PngDescriptionDLL

manager = PngDescriptionDLL.PngDescriptionManager()

try:
    path = os.path.normpath("D:\Main")
    print(f"파이썬 로그 파일 경로: {path}")
    description2:tuple[str, str] = manager.Load(path)
    if description2 is not None:
        for path, desc in description2:
            print(f"파이썬 로그 파일 경로: {path}, 설명: {desc}")
    else:
        print("Description not found.")

except RuntimeError as e:
    print(f"Error: {e}")
