from imagefileinfo import ImageFileInfo

class DataContainer:
    loaded_image_infos: list[ImageFileInfo] = []
    searched_image_infos: list[ImageFileInfo] = []
    search_keywords: list[str] = []
    
    @classmethod
    @property
    def search_images_count(cls):
        return len(cls.searched_image_infos)
    
    @classmethod
    @property
    def loaded_images_count(cls):
        return len(cls.loaded_image_infos)

    @classmethod
    def get_image_infos(cls):
        return cls.loaded_image_infos
    
    @classmethod
    def get_searched_image_infos(cls):
        return cls.searched_image_infos
    
    @classmethod
    def get_search_keywords(cls):
        return cls.search_keywords
    
    def get_searched_image_paths(cls):
        return [image_info.file_path for image_info in cls.searched_image_infos]
    
    @classmethod
    def add_image_info(cls, image_info: ImageFileInfo):
        cls.loaded_image_infos.append(image_info)

    @classmethod
    def add_searched_image_info(cls, image_info: ImageFileInfo):
        cls.searched_image_infos.append(image_info)

    @classmethod
    def add_search_keywords(cls, keywords: list[str]):
        cls.search_keywords.append(keywords)

    @classmethod
    def set_search_keywords(cls, keywords: list[str]):
        if len(cls.search_keywords) > 0:
            cls.search_keywords.clear()
        cls.search_keywords = keywords
        print(f"검색 키워드: {cls.search_keywords}")
    
    @classmethod
    def set_searched_image_infos(cls, image_infos: list[ImageFileInfo]):
        if len(cls.searched_image_infos) > 0:
            cls.searched_image_infos.clear()
        cls.searched_image_infos = image_infos
        print(f"검색된 이미지: {cls.search_images_count}개")

    @classmethod
    def set_loaded_image_infos(cls, image_infos: list[ImageFileInfo]):
        if len(cls.loaded_image_infos) > 0:
            print(f"기존 로드된 이미지를 지웠습니다. {cls.loaded_images_count}개")
            cls.loaded_image_infos.clear()
        cls.loaded_image_infos = image_infos
        print(f"로드된 이미지: {cls.loaded_images_count}개")

    
    @classmethod
    def clear(cls):
        cls.loaded_image_infos.clear()
        cls.searched_image_infos.clear()
        cls.search_keywords.clear()
        print("데이터 초기화 : 로드된 이미지, 검색된 이미지, 검색 키워드 초기화 완료!")