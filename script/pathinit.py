
import os
import sys

from .constants import IMAGE_FORMAT


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
    return os.path.join(base_path, relative_path)

def get_basic_save_path(program_start_path: str) -> str:
    """
    기본 저장 경로를 반환하는 함수
    """
    return os.path.join(program_start_path, "CreeperResult")

def get_program_start_path() -> str:
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

def check_folder_has_image(target_directory: str) -> bool:
    for _, _, files in os.walk(target_directory):
        for file in files:
            if check_is_image(file):
                return True
    return False

def check_is_image(filename: str) -> bool:
    return filename.lower().endswith(IMAGE_FORMAT)