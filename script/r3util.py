import json
import struct
from PIL import Image

from .optiondata import OptionData
from .stealth_pnginfo import read_info_from_image_stealth

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
                    elif key == "Comment":
                        value = value.decode('latin1')
                        prompt_data = json.loads(value)['prompt']
                        print(f"Description 추출: {filename}")
                        return (prompt_data, True)
            else:
                f.seek(chunk_length, 1)
            f.read(4)
    if OptionData.is_stealth_mode:
        with Image.open(filename) as img:
            tmp = read_info_from_image_stealth(img)
            if tmp:
                print(f"Util : Stealth 모드로 Description 추출:{filename}")
                desc = json.loads(tmp)['Description']
                return (desc, True)
    print(f"Util : Description이 없는 PNG 파일: {filename}")
    return (None, False)  # Description이 없는 경우

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