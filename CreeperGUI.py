from queue import Queue
import winsound
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QListWidget, QVBoxLayout, QLabel, QSizePolicy, QFileDialog, QDialog, QCheckBox, QListWidgetItem
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QPixmap

from datacontainer import DataContainer
from imagefileinfo import ImageFileInfo
from optiondata import OptionData
from r3util import HighlightingText

class CRSearchBar(QWidget):
    """
    검색 바 위젯
    """
    search_requested = pyqtSignal(str)

    def __init__(self):
        super().__init__()  # QWidget의 생성자를 호출합니다.

        # 레이아웃 설정
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        # 검색 바와 검색 버튼 설정
        self.search_bar = QLineEdit()
        search_button = QPushButton('검색')
        self.search_bar.returnPressed.connect(self.emit_search_requested)
        search_button.clicked.connect(self.emit_search_requested)

        # 위젯을 레이아웃에 추가합니다.
        self.layout.addWidget(self.search_bar)
        self.layout.addWidget(search_button)

    def emit_search_requested(self):
        self.search_requested.emit(self.search_bar.text())

    def clear(self):
        self.search_bar.clear()

class CRImageInfoListWidget(QWidget):
    """
    이미지 정보를 리스트로 표시하는 위젯
    """
    on_selected_image_changed = pyqtSignal(ImageFileInfo)
    on_clicked_option_button = pyqtSignal()
    on_clicked_move_files_button = pyqtSignal()
    on_user_delete_item = pyqtSignal()

    def __init__(self):
        super().__init__()
        # 레이아웃 설정
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(10, 0, 5, 0)

        self._undo_history: Queue[tuple[QListWidgetItem, int]]= Queue(maxsize=10)

        # 이미지 리스트 설정
        self.imageinfo_list_widget = QListWidget()
        self.imageinfo_list_widget.currentItemChanged.connect(self.emit_current_item_changed)
        self.imageinfo_list_widget.itemClicked.connect(self.emit_current_item_changed)
        self.imageinfo_list_widget.alternatingRowColors()
        self.imageinfo_list_widget.setSelectionMode(QListWidget.SingleSelection)
        self.imageinfo_list_widget.keyPressEvent = self.keyPressEvent
        # 리스트 위젯을 레이아웃에 추가합니다.
        self.layout.addWidget(self.imageinfo_list_widget)

        # 리스트 upper 레이아웃 설정
        list_up_layout = QHBoxLayout()

        self.move_files_button = QPushButton('결과 저장')
        self.move_files_button.setToolTip('검색된 이미지를 모아 폴더를 생성합니다. (기본 폴더 이름: 검색키워드_..._Copy/Move)')
        self.move_files_button.clicked.connect(self.emit_move_files_button_clicked)
        self.move_files_button.setDisabled(True)

        self.option_button = QPushButton('옵션')
        self.option_button.clicked.connect(self.emit_option_button_clicked)

        self.searched_images_count_label = QLabel('검색된 이미지 수: 0')
        self.searched_images_count_label.setAlignment(Qt.AlignRight)
        self.searched_images_count_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        list_up_layout.addWidget(self.move_files_button)
        list_up_layout.addWidget(self.option_button)
        list_up_layout.addWidget(self.searched_images_count_label)

        self.layout.addLayout(list_up_layout)
        self.layout.addWidget(self.imageinfo_list_widget)

    def emit_current_item_changed(self):
        if self.imageinfo_list_widget.currentItem() is None:
            return
        current_item_info: ImageFileInfo = self.imageinfo_list_widget.currentItem().data(Qt.UserRole)
        self.on_selected_image_changed.emit(current_item_info)

    def emit_option_button_clicked(self):
        self.on_clicked_option_button.emit()

    def emit_move_files_button_clicked(self):
        self.on_clicked_move_files_button.emit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.on_user_delete_item.emit()
            self._delete_item(self.imageinfo_list_widget.currentItem())
            self.searched_images_count_label.setText(f'검색된 이미지 수: {self.imageinfo_list_widget.count()}')
        elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier:
            self._undo_delete_item()
            self.searched_images_count_label.setText(f'검색된 이미지 수: {self.imageinfo_list_widget.count()}')
        else:
            QListWidget.keyPressEvent(self.imageinfo_list_widget, event)

    def update_list_widget(self, image_infos: list[ImageFileInfo]):
        self.imageinfo_list_widget.clear()
        for image_info in image_infos:
            item = QListWidgetItem()
            item.setText(f"{image_info.file_path}")
            item.setData(Qt.UserRole, image_info)
            self.imageinfo_list_widget.addItem(item)

        if len(image_infos) > 0:
            self.move_files_button.setDisabled(False)
        else:
            self.move_files_button.setDisabled(True)
        self.imageinfo_list_widget.sortItems(order=Qt.AscendingOrder)
        self.imageinfo_list_widget.scrollToTop()
        self.searched_images_count_label.setText(f'검색된 이미지 수: {len(image_infos)}')

    def get_imageinfos(self) -> set[ImageFileInfo]:
        result: set[ImageFileInfo] = set()
        for index in range(self.imageinfo_list_widget.count()):
            item = self.imageinfo_list_widget.item(index)
            image_info: ImageFileInfo = item.data(Qt.UserRole)
            result.add(image_info)
        return result

    def clear(self):
        self.imageinfo_list_widget.clear()
        self.searched_images_count_label.setText('검색된 이미지 수: 0')
        self.move_files_button.setDisabled(True)

    def _delete_item(self, delete_item: QListWidgetItem):
        delete_index: int = self.imageinfo_list_widget.row(delete_item)
        self.imageinfo_list_widget.takeItem(delete_index)
        delete_data: tuple[QListWidgetItem, int] = (delete_item, delete_index)
        if not self._undo_history.full():
            self._undo_history.put(delete_data)
        else:
            self._undo_history.get()
            self._undo_history.put(delete_data)

    def _undo_delete_item(self):
        if not self._undo_history.empty():
            undo_data: tuple = self._undo_history.get()
            item, index = undo_data
            if item is not None and index is not None:
                self.imageinfo_list_widget.insertItem(index, item)
                self.imageinfo_list_widget.scrollToItem(item)
                self.imageinfo_list_widget.setCurrentItem(item)
        else:
            print("삭제 이력이 없습니다.")

class CRImageContainer(QWidget):
    """
    이미지를 표시하는 위젯
    """
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(5, 0, 10, 0)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(512, 512)

        self.layout.addWidget(self.image_label)

    def set_image(self, image_path: str):
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)

    def clear(self):
        self.image_label.clear()

class CRInfoWidget(QWidget):
    """
    이미지 설명을 표시하는 위젯
    """
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(10, 10, 10, 0)

        self.info_label = QLabel()
        self.info_label.setTextFormat(Qt.RichText)
        self.info_label.setAlignment(Qt.AlignLeft)
        self.info_label.setWordWrap(True)
        self.info_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.info_label.setFixedHeight(100)

        self.layout.addWidget(self.info_label)

    def set_info_text(self, image_desc: str):
        highlighted_desc = HighlightingText(image_desc, DataContainer.search_keywords)
        self.info_label.setText(highlighted_desc)

    def clear(self):
        self.info_label.clear()

class CRPathSelectWidget(QWidget):
    """
    경로 선택 위젯
    """
    on_path_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.path_label = QLabel('선택된 경로 없음 ( 이미지가 존재하는 폴더를 선택하세요. )')
        self.count_label = QLabel('로드된 이미지 수: 0')
        path_button = QPushButton('경로 선택')
        path_button.clicked.connect(self.choose_path)

        self.layout.addWidget(self.path_label, 7)  # 비율 설정
        self.layout.addWidget(path_button, 2)  # 비율 설정
        self.layout.addWidget(self.count_label, 1)  # 비율 설정

    def choose_path(self):
        selected_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if selected_path:
            self.on_path_selected.emit(selected_path)

    def set_path_label(self, path: str):
        self.path_label.setText(path)

    def update_count_label(self, count: int):
        self.count_label.setText(f'로드된 이미지 수: {count}')

class CROptionDialog(QDialog):
    """
    옵션 설정 다이얼로그
    """
    def __init__(self, parent: QMainWindow=None):
        self._init_option_layout(parent)

    def accept(self):
        save_path = self.save_path_data_label.text()
        save_option = self.save_option_data_checkbox.isChecked()
        OptionData.update_save_data(save_path, save_option)
        super().accept()

    def reject(self):
        print("옵션 저장 취소")
        super().reject()
    
    def _select_save_path(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.save_path_data_label.setText(directory)

    def _init_option_layout(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("옵션")
        self.setParent(parent)
        self.setWindowModality(2)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint | Qt.CustomizeWindowHint)
        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        option_layout = QVBoxLayout()

        main_layout.addLayout(option_layout)
        main_layout.addLayout(button_layout)

        # 옵션 속성1
        option1_layout = QHBoxLayout()
        self.save_path_option_label = QLabel("저장위치 :")
        self.save_path_data_label = QLabel(f"{OptionData.save_path}")
        self.save_path_data_label.setStyleSheet("background-color: #444; color: #FFF;")
        self.save_path_data_label.setFixedHeight(30)
        self.save_path_select_button = QPushButton("경로 선택")
        self.save_path_select_button.setFixedHeight(30)
        self.save_path_select_button.clicked.connect(self._select_save_path)
        option1_layout.addWidget(self.save_path_option_label)
        option1_layout.addWidget(self.save_path_data_label)
        option1_layout.addWidget(self.save_path_select_button)
        # 옵션 속성2
        option2_layout = QHBoxLayout()
        self.save_option_label = QLabel("파일 복사 모드 :")
        self.save_option_label.setToolTip("해당 옵션이 활성화 되어있을 경우, 검색된 이미지를 복사합니다. 비활성화 되어있을 경우, 이동합니다.")
        self.save_option_label.setFixedHeight(30)
        self.save_option_data_checkbox = QCheckBox()
        self.save_option_data_checkbox.setChecked(OptionData.is_copy_mode)
        self.save_option_data_checkbox.setFixedHeight(30)
        option2_layout.addWidget(self.save_option_label)
        option2_layout.addWidget(self.save_option_data_checkbox)

        # 옵션 레이아웃에 추가
        option_layout.addLayout(option1_layout)
        option_layout.addLayout(option2_layout)

        # OK와 Cancel 버튼
        self.ok_button = QPushButton("OK", self)
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)

        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.setLayout(main_layout)

class CRPopupWindow(QDialog):
    parent = None

    Info = 0
    Warning = 1
    Error = 2

    _popup_title = {
        Info: "알림",
        Warning: "경고",
        Error: "오류"
    }

    _popup_sound = {
        Info: "SystemAsterisk",
        Warning: "SystemExclamation",
        Error: "SystemHand"
    }

    def __init__(self, parent):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.setWindowTitle("알림")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint | Qt.CustomizeWindowHint)
        self.setWindowModality(2)
        self.setMinimumWidth(150)
        self.setStyleSheet("""
        QLabel {
            padding: 10px;
        }
        """)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)

        self.ok_button = QPushButton("확인")
        self.ok_button.clicked.connect(self.accept)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.ok_button)

    def accept(self):
        super().accept()

    @staticmethod
    def show(message: str, popup_type: int, parent=None):
        """
        팝업을 표시하는 함수
        :param message: 표시할 메시지
        :param popup_type: 팝업 타입
        :param parent: 부모 위젯 (기본값은 MainGui의 인스턴스)
        """
        if parent == None:
            parent = CRPopupWindow.parent

        popup = CRPopupWindow(parent)
        popup.set_type(popup_type)
        popup.label.setText(message)
        popup.setFixedSize(popup.sizeHint().width(), popup.sizeHint().height())
        sound_name = CRPopupWindow._popup_sound.get(popup_type, "SystemAsterisk")
        winsound.PlaySound(sound_name, winsound.SND_ASYNC | winsound.SND_ALIAS)
        popup.exec()


    def set_type(self, popup_type: int):
        type_text = CRPopupWindow._popup_title.get(popup_type, "알림")
        self.setWindowTitle(type_text)

    @staticmethod
    def set_main_window(main_window):
        CRPopupWindow.parent = main_window