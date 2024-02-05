import os
from datacontainer import DataContainer
from optiondata import OptionData
from imagefileinfo import ImageFileInfo

from r3util import search_with_listfind, boyer_moore, check_is_image, get_png_description

class DataManager:
    # 이미지 정보를 DataContainer에 로드하는 함수
    @staticmethod
    def load_image_infos():
        DataContainer.clear()
        search_images_count: int = 0
        tmp_image_infos: list[ImageFileInfo] = []
        for root, _, files in os.walk(OptionData.load_path):
            for file in files:
                if check_is_image(file):
                    search_images_count += 1
                    file_path = os.path.join(root, file)
                    description, is_acessable = get_png_description(file_path)
                    if not is_acessable:
                        continue
                    image_info = ImageFileInfo(file_path, description)
                    tmp_image_infos.append(image_info)
                    print(f'현재 로드한 이미지 : {search_images_count}개 / {file_path}')

        DataContainer.set_loaded_image_infos(tmp_image_infos)

    # 검색 키워드(,로 구분)를 받아 이미지를 검색하는 함수
    @staticmethod
    def search_images(search_text: str):
        DataContainer.searched_image_infos.clear()
        DataContainer.search_keywords = [keyword.strip().lower() for keyword in search_text.split(',')]
        print(f'검색 키워드: {DataContainer.search_keywords}')

        result: list[ImageFileInfo] = []

        search_keywords = DataContainer.search_keywords
        # 로드된 이미지들을 전부 검색
        for image_info in DataContainer.loaded_image_infos:
            match = True
            for keyword in search_keywords:
                if keyword.startswith('~'):
                    # '~'로 시작하는 키워드: _search_with_listfind 함수 사용
                    exact_keyword = keyword[1:]
                    if not search_with_listfind(image_info.file_info_list, exact_keyword):
                        match = False
                        break
                else:
                    # '~'로 시작하지 않는 키워드: Boyer-Moore 알고리즘 사용
                    if keyword == '':
                        continue
                    elif not boyer_moore(image_info.file_info, keyword):
                        match = False
                        break
                    
            if match:
                result.append(image_info)
        DataContainer.searched_image_infos = result
        print(f'검색 결과: {DataContainer.search_images_count}개')
        return result