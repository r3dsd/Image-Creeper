import os
import shutil
from optiondata import OptionData
from imagefileinfo import ImageFileInfo
from datacontainer import DataContainer
from CreeperGUI import CRPopupWindow
from constants import MAX_FILE_NAME_LENGTH

class FileManager:
    @staticmethod
    def image_files_to_save_folder(target_file_list: list[str]):
        """
        검색된 이미지를 저장 경로로 이동하는 함수
        :param target_file_list: 이동할 이미지 파일 리스트
        """
        is_copy_mode = OptionData.is_copy_mode
        save_folder_path = get_save_path(is_copy_mode=is_copy_mode, search_keywords=DataContainer.search_keywords)
        if is_copy_mode:
            copy_files(target_file_list, save_folder_path)
        else:
            move_files(target_file_list, save_folder_path)

        return save_folder_path

# 검색된 이미지를 저장 경로로 이동하는 함수
def move_files(target_file_list: set[ImageFileInfo], save_folder_path: str):
    for target_image_info in target_file_list:
        source_file_path: str = target_image_info.file_path
        file_name, file_extension = os.path.splitext(target_image_info.file_name)

        # 파일 이름에 넘버링 추가
        counter = 1
        new_file_name = f"{file_name}_{counter}"
        destination_file_path = os.path.join(save_folder_path, new_file_name + file_extension)

        # 같은 이름이 있는 경우에만 넘버링 증가
        while os.path.exists(destination_file_path):
            counter += 1
            new_file_name = f"{file_name}_{counter}"
            destination_file_path = os.path.join(save_folder_path, new_file_name + file_extension)

        shutil.move(source_file_path, destination_file_path)
        print(f'파일 이동: {source_file_path} -> {destination_file_path}')
    DataContainer.delete_loaded_image_infos(target_file_list)
    CRPopupWindow.show_with_folder_open_button("이미지가 이동되었습니다.", save_folder_path)

# 검색된 이미지를 저장 경로에 복사하는 함수
def copy_files(target_file_list: set[ImageFileInfo], save_folder_path: str):
    for target_image_info in target_file_list:
        source_file_path: str = target_image_info.file_path
        file_name, file_extension = os.path.splitext(target_image_info.file_name)

        # 파일 이름에 넘버링 추가
        counter = 1
        new_file_name = f"{file_name}_{counter}"
        destination_file_path = os.path.join(save_folder_path, new_file_name + file_extension)

        # 같은 이름이 있는 경우에만 넘버링 증가
        while os.path.exists(destination_file_path):
            counter += 1
            new_file_name = f"{file_name}_{counter}"
            destination_file_path = os.path.join(save_folder_path, new_file_name + file_extension)

        shutil.copy(source_file_path, destination_file_path)
        print(f'파일 복사: {source_file_path} -> {destination_file_path}')
    CRPopupWindow.show_with_folder_open_button("이미지가 복사되었습니다.", save_folder_path)

# 저장 경로를 반환하는 함수
def get_save_path(is_copy_mode: bool, search_keywords: list[str]):
    save_path: str = OptionData.save_path
    mode_text = '_Copy' if is_copy_mode else '_Move'

    keywords_text = '_'.join(search_keywords)
    if len(keywords_text) > MAX_FILE_NAME_LENGTH:
        keywords_text = keywords_text[:MAX_FILE_NAME_LENGTH-3] + "..."

    destination_folder_name: str = keywords_text + mode_text
    save_folder_path: str = os.path.join(save_path, destination_folder_name)

    # 동일한 폴더 이름이 존재하는 경우 넘버링 추가
    counter = 1
    original_save_folder_path = save_folder_path
    while os.path.exists(save_folder_path):
        save_folder_path = f"{original_save_folder_path} ({counter})"
        counter += 1

    os.makedirs(save_folder_path)
    print(f'폴더 생성: {save_folder_path}')

    return save_folder_path