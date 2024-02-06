import os
import struct
import sys

from constants import IMAGE_FORMAT

def boyer_moore(text: str, pattern: str):
    text_length = len(text)
    pattern_length = len(pattern)
    skip = []
    if pattern_length == 0:
        return False
    # 휴리스틱 함수 계산
    for i in range(256):
        skip.append(pattern_length)
    for i in range(pattern_length - 1):
        skip[ord(pattern[i])] = pattern_length - i - 1
    # 검색
    i = pattern_length - 1
    while i < text_length:
        j = pattern_length - 1
        k = i
        while j >= 0 and text[k] == pattern[j]:
            j -= 1
            k -= 1
        if j == -1:
            return True
        i += skip[ord(text[i])]
    return False

def search_with_listfind(text_list: list[str], pattern: str):
    for text in text_list:
        if text == pattern:
            return True
    return False

def get_program_start_path():
    """
    프로그램 시작 경로를 반환하는 함수
    """
    if getattr(sys, 'frozen', False):
        # pyinstaller로 빌드된 실행 파일의 경우
        main_path = os.path.dirname(sys.executable)
    else:
        # 일반적인 파이썬 스크립트 실행의 경우
        main_path = os.path.dirname(os.path.abspath(__file__))
    print(f"Util : 프로그램 시작 경로: {main_path}")
    return main_path

def get_basic_save_path(program_start_path: str):
    """
    기본 저장 경로를 반환하는 함수
    """
    return os.path.join(program_start_path, "CreeperResult")

# directory에 이미지가 있는지 확인하는 함수
def check_folder_has_image(target_directory: str):
    for _, _, files in os.walk(target_directory):
        for file in files:
            if check_is_image(file):
                return True
    return False

def check_is_image(filename: str):
    return filename.lower().endswith(IMAGE_FORMAT)

# PNG 파일의 Description 메타데이터를 가져오는 함수 (PIL 사용)
# def get_png_description_pil(filename: str) -> (str, bool):
#     if check_is_image(filename):
#         with Image.open(filename) as img:
#             description = img.info.get('Description', None)
#             if description:
#                 return (description, True)
#             else:
#                 return (None, False)

# PNG 파일의 Description 메타데이터를 가져오는 함수 (PIL 미사용)
def get_png_description(filename) -> (str, bool):
    with open(filename, 'rb') as f:
        if f.read(8) != b'\x89PNG\r\n\x1a\n':
            raise ValueError("Not a valid PNG file")

        while True:
            chunk_length, chunk_type = struct.unpack(">I4s", f.read(8))
            if chunk_type == b'IEND':
                break

            # tEXt 청크 처리
            if chunk_type == b'tEXt':
                data = f.read(chunk_length)
                parts = data.split(b'\x00', 1)
                if len(parts) == 2:
                    key, value = parts
                    key = key.decode('latin1')
                    if key == "Description":
                        value = value.decode('latin1')
                        print(f"Description 추출: {filename}")
                        return (value, True)
            else:
                f.seek(chunk_length, 1)
            f.read(4)
    print(f"Util : Description이 없는 PNG 파일: {filename}")
    return (None, False)  # Description이 없는 경우

def get_resource_path(relative_path: str):
    """
    올바른 리소스 경로를 반환하는 함수
    """
    if getattr(sys, 'frozen', False):
        # pyinstaller로 빌드된 실행 파일의 경우
        base_path = sys._MEIPASS
    else:
        # 일반적인 파이썬 스크립트 실행의 경우
        base_path = os.path.abspath(".")
    print(f"Util : 리소스 경로: {os.path.join(base_path, relative_path)}")
    return os.path.join(base_path, relative_path)

def HighlightingText(text: str, keywords: list[str]):
    # 텍스트를 쉼표와 공백을 기준으로 단어 단위로 분리
    words = [text.strip() for text in text.split(',')]

    for i in range(len(words)):
        for keyword in keywords:
            if keyword.startswith('~'):
                # 완전일치 검사
                if words[i] == keyword[1:]:
                    words[i] = "<span style='background-color: #0F0'>" + words[i] + "</span>"
            else:
                # 부분일치 검사
                if keyword in words[i]:
                    words[i] = words[i].replace(keyword, "<span style='background-color: #F00'>" + keyword + "</span>")

    # 강조된 단어들을 다시 조합
    return ', '.join(words)