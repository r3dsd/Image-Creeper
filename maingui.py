from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSignal, QObject, QThread

from CreeperGUI import CRPathSelectWidget, CRSearchBar, CRImageInfoListWidget, CRImageContainer, CRInfoWidget, CRPopupWindow, CROptionDialog
from filemanager import FileManager
from datamanager import DataManager

from datacontainer import DataContainer
from optiondata import OptionData
from imagefileinfo import ImageFileInfo

from constants import PROGRAM_NAME, PROGRAM_VERSION, GUI_STYLE_SHEET
from r3util import get_resource_path

class MainGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        OptionData.option_data_load_with_json()
        self.initUI()

    def initUI(self):
        # 메인 윈도우 설정
        self._init_main_window()
        # 전체 레이아웃
        main_layout: QVBoxLayout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        upper_layout: QHBoxLayout = self._init_upper_layout()
        upper_layout.setContentsMargins(0, 0, 0, 0)
        upper_layout.setSpacing(0)
        middle_layout: QHBoxLayout = self._init_middle_layout()
        middle_layout.setContentsMargins(0, 0, 0, 0)
        middle_layout.setSpacing(0)
        bottom_layout: QHBoxLayout = self._init_bottom_layout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(0)
        # 레이아웃 추가
        main_layout.addLayout(upper_layout)
        main_layout.addLayout(middle_layout)
        main_layout.addLayout(bottom_layout)
        # 중앙 위젯 생성
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        main_widget.setContentsMargins(0, 0, 0, 0)
        # 중앙 위젯을 메인 윈도우의 중앙 위젯으로 설정
        self.setCentralWidget(main_widget)
        self.show()
        # 옵션 패널 
        self.optionPanel = CROptionDialog(self)

    def on_search_requested(self, search_text: str):
        self.search_start(search_text)

    def on_selected_image_changed(self, image_info: ImageFileInfo):
        self.update_image_info(image_info)

    def on_clicked_option_button(self):
        self.optionPanel.show()

    def on_clicked_move_files_button(self):
        if not OptionData.is_loaded():
            CRPopupWindow.show("로드된 이미지가 없습니다.", CRPopupWindow.Warning, self)
            return

        selected_image_infos: set[ImageFileInfo] = self.image_info_list_widget.get_imageinfos()
        
        final_save_path = FileManager.image_files_to_save_folder(selected_image_infos)

        if not OptionData.is_copy_mode:
            self.image_view_container.clear()
            self.image_info_list_widget.clear()
        self.info_widget.set_info_text(f"이미지가 저장되었습니다. <br>저장 경로 : {final_save_path}")

    def on_path_selected(self, path: str):
        if path == '':
            return

        self.info_widget.set_info_text("이미지 로드 중... 잠시만 기다려주세요.")
        if OptionData.set_load_path(path):
            self.path_widget.set_path_label(path)
            self.thread = QThread()
            self.image_loader = ImageLoader()
            self.image_loader.moveToThread(self.thread)
            self.thread.started.connect(self.image_loader.run)
            self.image_loader.finished.connect(self.on_image_load_finished)
            self.thread.start()

    def on_image_load_finished(self):
        self.path_widget.update_count_label(DataContainer.loaded_images_count)
        self.info_widget.set_info_text('''
            <p>이미지 로드 완료. 검색어를 입력하세요.<br>
            1. 태그는 쉼표로 구분하여 여러개 입력 가능합니다.<br>
            2. 태그는 대소문자를 구분합니다.<br>
            3. 태그는 부분일치 검색됩니다.<br>
            4. ~를 입력하여 완전일치하는 태그를 검색할 수 있습니다.</p>
        ''')
        self.thread.quit()
        self.thread.wait()

    def on_user_delete_item(self):
        self.image_view_container.clear()
        self.info_widget.clear()

    def search_start(self, search_text: str):
        """
        검색 시작 함수
        :param search_text: 검색어
        """
        if OptionData.is_loaded() == False:
            CRPopupWindow.show("로드된 이미지가 없습니다.", CRPopupWindow.Warning, self)
            return
        elif search_text == '':
            CRPopupWindow.show("검색어를 입력하세요.", CRPopupWindow.Warning, self)
            return

        image_infos : list[ImageFileInfo] = DataManager.search_images(search_text)
        self._on_search_completed(image_infos)

    def _on_search_completed(self, image_infos: list[ImageFileInfo]):
        """
        검색이 완료된 후의 처리 함수
        :param image_infos: 검색된 이미지 정보 리스트
        """
        if len(image_infos) == 0:
            self.info_widget.set_info_text("검색 결과가 없습니다.")
            self.image_info_list_widget.clear()
            self.image_view_container.clear()
            return
        self.image_info_list_widget.update_list_widget(image_infos)
        self.image_view_container.clear()
        self.info_widget.set_info_text(f"검색 완료. 목록을 클릭하면 상세정보를 확인할 수 있습니다.")
    
    def update_image_info(self, image_info: ImageFileInfo):
        """
        이미지 정보(태그, 이미지)를 업데이트하는 함수
        :param image_info: 전달된 이미지 정보"""
        if image_info is None:
            return
        self.info_widget.set_info_text(image_info.file_info)
        self.image_view_container.set_image(image_info.file_path)
    
    def _clear_widgets(self):
        self.image_info_list_widget.clear()
        self.image_view_container.clear()
        self.info_widget.clear()

    """레이아웃 초기화 함수들"""
    def _init_main_window(self):
        self.setWindowTitle(f'{PROGRAM_NAME} {PROGRAM_VERSION}')
        icon_path = get_resource_path('icon.ico')
        self.setWindowIcon(QIcon(icon_path))
        print(f"{PROGRAM_NAME} {PROGRAM_VERSION} Started")
        self.setGeometry(100, 100, 1200, 600)
        self.setStyleSheet(GUI_STYLE_SHEET)

    def _init_upper_layout(self):
        upper_layout: QHBoxLayout = QHBoxLayout()
        # 검색 바 위젯
        self.search_bar: CRSearchBar = CRSearchBar()
        self.search_bar.search_requested.connect(self.on_search_requested)
        upper_layout.addWidget(self.search_bar)

        return upper_layout

    def _init_middle_layout(self):
        middle_layout: QHBoxLayout = QHBoxLayout()
        # 이미지 정보 리스트 위젯
        self.image_info_list_widget: CRImageInfoListWidget = CRImageInfoListWidget()
        self.image_info_list_widget.on_selected_image_changed.connect(self.on_selected_image_changed)
        self.image_info_list_widget.on_clicked_move_files_button.connect(self.on_clicked_move_files_button)
        self.image_info_list_widget.on_clicked_option_button.connect(self.on_clicked_option_button)
        self.image_info_list_widget.on_user_delete_item.connect(self.on_user_delete_item)

        # 이미지 미리보기 위젯
        self.image_view_container: CRImageContainer = CRImageContainer()

        # 이미지 미리보기 위젯을 레이아웃에 추가 (중앙 좌측에 위치)
        image_list_layout: QVBoxLayout = QVBoxLayout()
        image_list_layout.setContentsMargins(0, 0, 0, 0)
        image_list_layout.setSpacing(0)
        image_list_layout.addWidget(self.image_info_list_widget)

        # 이미지 정보 리스트 위젯을 레이아웃에 추가 (중앙 우측에 위치)
        image_view_container_layout: QVBoxLayout = QVBoxLayout()
        image_view_container_layout.setContentsMargins(0, 0, 0, 0)
        image_view_container_layout.setSpacing(0)
        image_view_container_layout.addWidget(self.image_view_container)
        
        # 이미지 정보 리스트 위젯과 이미지 미리보기 위젯을 중앙 레이아웃에 추가
        middle_layout.addLayout(image_list_layout, 5)
        middle_layout.addLayout(image_view_container_layout, 5)

        return middle_layout
    
    def _init_bottom_layout(self):
        bottom_layout: QVBoxLayout = QVBoxLayout()
        
        # 정보 표시 레이아웃
        self.info_widget = CRInfoWidget()
        bottom_layout.addWidget(self.info_widget)

        # 경로 선택 레이아웃
        self.path_widget = CRPathSelectWidget()
        self.path_widget.on_path_selected.connect(self.on_path_selected)
        bottom_layout.addWidget(self.path_widget)

        return bottom_layout
    

class ImageLoader(QObject):
    finished = pyqtSignal()

    def run(self):
        DataManager.load_image_infos(OptionData.load_path)
        self.finished.emit()