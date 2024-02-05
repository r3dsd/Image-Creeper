from imagefileinfo import ImageFileInfo

class DataContainer:
    loaded_image_infos: set[ImageFileInfo] = []
    search_keywords: list[str] = []
    
    @classmethod
    @property
    def loaded_images_count(cls):
        return len(cls.loaded_image_infos)

    @classmethod
    def get_image_infos(cls):
        return cls.loaded_image_infos
    
    @classmethod
    def get_search_keywords(cls):
        return cls.search_keywords
    
    @classmethod
    def add_image_info(cls, image_info: ImageFileInfo):
        cls.loaded_image_infos.add(image_info)

    @classmethod
    def delete_loaded_image_infos(cls, image_infos: set[ImageFileInfo]):
        before_count = cls.loaded_images_count
        cls.loaded_image_infos.difference_update(image_infos)
        print(f"파일이 이동되었습니다. {before_count}개 -> {cls.loaded_images_count}개")

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
    def set_loaded_image_infos(cls, image_infos: set[ImageFileInfo]):
        if len(cls.loaded_image_infos) > 0:
            print(f"기존 로드된 이미지를 지웠습니다. {cls.loaded_images_count}개")
            cls.loaded_image_infos.clear()
        cls.loaded_image_infos = image_infos
        print(f"로드된 이미지: {cls.loaded_images_count}개")
    
    @classmethod
    def clear(cls):
        cls.loaded_image_infos.clear()
        cls.search_keywords.clear()
        print("데이터 초기화 : 로드된 이미지, 검색된 이미지, 검색 키워드 초기화 완료!")