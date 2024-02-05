import os
from dataclasses import dataclass

@dataclass
class ImageFileInfo:
    file_path: str
    file_info: str # 이미지 파일 태그 정보

    def __post_init__(self):
        self.file_name: str = os.path.basename(self.file_path)
        self.file_info_list: list[str] = [info.strip().lower() for info in self.file_info.split(',')]

    def __str__(self):
        return f"{self.file_path}"
    
    def __hash__(self) -> int:
        return hash(self.file_path)
    
    def __eq__(self, other) -> bool:
        if other is None:
            return False
        if isinstance(other, self.__class__):
            return self.file_path == other.file_path
        return False
