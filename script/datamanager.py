import os
from .datacontainer import DataContainer
from .imagefileinfo import ImageFileInfo

import concurrent.futures

from .r3util import search_with_listfind, boyer_moore, check_is_image, get_png_description


class DataManager:
    # 이미지 정보를 DataContainer에 로드하는 함수
    # @staticmethod
    # def load_image_infos_single_thread(file_path: str):
    #     DataContainer.clear()
    #     search_images_count: int = 0
    #     tmp_image_infos: list[ImageFileInfo] = []
    #     for root, _, files in os.walk(file_path):
    #         for file in files:
    #             if check_is_image(file):
    #                 search_images_count += 1
    #                 file_path = os.path.join(root, file)
    #                 description, is_acessable = get_png_description(file_path)
    #                 if not is_acessable:
    #                     continue
    #                 image_info = ImageFileInfo(file_path, description)
    #                 tmp_image_infos.append(image_info)
    #                 print(f'현재 로드한 이미지 : {search_images_count}개 / {file_path}')

    #     DataContainer.set_loaded_image_infos(tmp_image_infos)

    @staticmethod
    def load_image_infos(path: str):
        DataContainer.clear()

        def process_file(file_path):
            description, is_acessable = get_png_description(file_path)
            if is_acessable:
                return ImageFileInfo(file_path, description)
            return None

        print(f'이미지 로드 시작: {path}')
        files_to_process = []
        for root, _, files in os.walk(path):
            for file in files:
                if check_is_image(file):
                    file_path = os.path.join(root, file)
                    files_to_process.append(file_path)

        max_workers = os.cpu_count()
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = set(executor.map(process_file, files_to_process))

        tmp_image_infos = {result for result in results if result is not None}
        for image_info in tmp_image_infos:
            for tag in image_info.file_info_list:
                DataContainer.add_database(tag)
        print(f'이미지 태그 데이터베이스: {len(DataContainer.search_tag_database)}개')
        DataContainer.set_loaded_image_infos(tmp_image_infos)

    # 검색 키워드(,로 구분)를 받아 이미지를 검색하는 함수
    @staticmethod
    def search_images(search_text: str):
        DataContainer.set_search_keywords([keyword.strip().lower() for keyword in search_text.split(',')])
        result: set[ImageFileInfo] = set()
        original_search_keywords = DataContainer.get_search_keywords()

        copy_search_keywords = original_search_keywords.copy()

        normal_keywords = []
        negated_keywords = []
        exact_keywords = []
        negated_exact_keywords = []

        while copy_search_keywords:
            keyword = copy_search_keywords.pop(0)
            if keyword.startswith('~!'):
                negated_exact_keywords.append(keyword[2:])
            elif keyword.startswith('~'):
                exact_keywords.append(keyword[1:])
            elif keyword.startswith('!'):
                negated_keywords.append(keyword[1:])
            else:
                normal_keywords.append(keyword)

        print(f'일반 키워드: {normal_keywords}')
        print(f'완전일치 키워드: {exact_keywords}')
        print(f'부정 키워드: {negated_keywords}')
        print(f'완전일치 부정 키워드: {negated_exact_keywords}')

        # 로드된 이미지들을 전부 검색
        for image_info in DataContainer.get_image_infos():
            match = True

            # 일반 키워드 검색
            for keyword in normal_keywords:
                if keyword and not boyer_moore(image_info.file_info, keyword):
                    match = False
                    break

            if match:
                # 부정 키워드 검색
                for keyword in negated_keywords:
                    if boyer_moore(image_info.file_info, keyword):
                        match = False
                        break

            if match:
                # 완전일치 검색
                for keyword in exact_keywords:
                    if not search_with_listfind(image_info.file_info_list, keyword):
                        match = False
                        break

            if match:
                # 완전일치 부정 검색
                for keyword in negated_exact_keywords:
                    if search_with_listfind(image_info.file_info_list, keyword):
                        match = False
                        break
            if match:
                    result.add(image_info)
        print(f'검색 결과: {len(result)}개')
        return result
    
    @staticmethod
    def get_search_database():
        return DataContainer.search_tag_database

# imgdata = set()
# imgdata.add(ImageFileInfo("1", "white shirt, blue pants, red shoes, green hat, yellow socks, black gloves"))
# imgdata.add(ImageFileInfo("2", "black shirt, red pants, green shoes, yellow hat, blue socks"))
# imgdata.add(ImageFileInfo("3", "yellow shirt, green pants, blue shoes, white hat, black socks, red gloves"))
# imgdata.add(ImageFileInfo("4", "red shirt, yellow pants, black shoes, green hat, white socks, blue gloves"))
# imgdata.add(ImageFileInfo("5", "green shirt, white pants, yellow shoes, red hat, blue socks, black gloves, z"))
# imgdata.add(ImageFileInfo("6", "blue shirt, black pants, white shoes, yellow hat, red socks, green gloves, z"))
# imgdata.add(ImageFileInfo("7", "black shirt, white pants, blue shoes, green hat, red socks, yellow gloves, z"))

# DataContainer.set_loaded_image_infos(imgdata)

# search_result = DataManager.search_images("blue, !gloves")

# for image_info in search_result:
#     print(image_info.file_path)

# print(DataContainer.search_keywords)