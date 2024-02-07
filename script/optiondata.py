import json
from .r3util import get_program_start_path, get_basic_save_path, check_folder_has_image

class OptionData:
    program_start_path: str = get_program_start_path()
    load_path: str = None
    save_path: str = get_basic_save_path(program_start_path)
    is_copy_mode: bool = True

    @classmethod
    def init(cls):
        cls.load_path = None
        cls.save_path = get_basic_save_path(cls.program_start_path)
        cls.is_copy_mode = True
        print(f"""--옵션 데이터 초기화--
이미지 폴더 경로: None
저장 경로: {cls.save_path}
복사모드: {cls.is_copy_mode}""")

    @classmethod
    def get_save_option(cls):
        return cls.save_path, cls.is_copy_mode
    
    @classmethod
    def get_load_path(cls):
        return cls.load_path
    
    @classmethod
    def set_save_path(cls, path: str):
        cls.save_path = path
        print(f"저장 경로 변경: {cls.save_path}")
    
    @classmethod
    def set_load_path(cls, path: str):
        has_image: bool = check_folder_has_image(path)
        if has_image:
            cls.load_path = path
        else:
            cls.load_path = ''
        print(f"로드 경로 설정됨: {cls.load_path}")

        return has_image
    
    @classmethod
    def set_copy_mode(cls, is_copy_mode: bool):
        cls.is_copy_mode = is_copy_mode
        print(f"복사 모드 변경: {cls.is_copy_mode}")

    @classmethod
    def update_save_data(cls, save_path: str, is_copy_mode: bool):
        cls.save_path = save_path
        cls.is_copy_mode = is_copy_mode
        print(f"옵션 데이터 변경: {cls.save_path}, {cls.is_copy_mode}")
        cls.option_data_save_with_json()

    @classmethod
    def is_loaded(cls):
        return cls.load_path != None and cls.load_path != ''

    @classmethod
    def option_data_save_with_json(cls):
        data = {
            "save_path": cls.save_path,
            "save_mode": cls.is_copy_mode,
        }
        with open("option.json", "w") as f:
            json.dump(data, f)
        print(f"옵션 데이터 저장 완료! 저장 경로: {cls.save_path}, 복사 모드: {cls.is_copy_mode}")

    @classmethod
    def option_data_load_with_json(cls):
        print("옵션 데이터를 로드중...")
        try:
            with open("option.json", "r") as file:
                data = json.load(file)
                cls.save_path = data.get('save_path', cls.save_path)
                cls.is_copy_mode = data.get('save_mode', cls.is_copy_mode)
                print(f"옵션 데이터 로드 완료! 저장 경로: {cls.save_path}, 복사 모드: {cls.is_copy_mode}")
        except FileNotFoundError:
            print("옵션 데이터 파일이 없습니다. 새로운 옵션 파일을 생성합니다.")
            cls.init()
            cls.option_data_save_with_json()