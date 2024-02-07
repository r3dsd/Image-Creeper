import os
import winsound
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QListWidget, QVBoxLayout, QLabel, QSizePolicy, QFileDialog, QDialog, QCheckBox, QListWidgetItem
from PyQt5.QtCore import pyqtSignal, Qt, QStringListModel
from PyQt5.QtWidgets import QMainWindow, QCompleter
from PyQt5.QtGui import QPixmap

from .datacontainer import DataContainer
from .filemanager import FileManager
from .imagefileinfo import ImageFileInfo
from .optiondata import OptionData
from .r3util import HighlightingText
from .CRhistorymanager import CRhistoryManager

class CRSearchBar(QWidget):
    """
    검색 바 위젯
    signal: search_requested(str)
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

    def update_search_model(self):
        search_model = QStringListModel()
        search_model.setStringList(DataContainer.search_tag_database)
        completer = QCompleter()
        completer.popup().setStyleSheet("background-color: #333; color: #FFF;")
        completer.setModel(search_model)
        self.search_bar.setCompleter(completer)

class CRImageListWidget(QWidget):
    """
    이미지 정보를 리스트로 표시하는 위젯
    """
    on_selected_image_changed = pyqtSignal(ImageFileInfo)
    on_user_delete_item = pyqtSignal()
    on_selected_list_changed = pyqtSignal(bool)
    on_deleted_search_list = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        # 레이아웃 설정
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(10, 0, 5, 0)

        # 좌측 이미지 리스트 설정
        list_widget_layout = QHBoxLayout()
        self.searched_imageinfo_list_widget = QListWidget()
        self.searched_imageinfo_list_widget.currentItemChanged.connect(self._emit_current_item_changed)
        self.searched_imageinfo_list_widget.itemClicked.connect(self._emit_current_item_changed)
        self.searched_imageinfo_list_widget.alternatingRowColors()
        self.searched_imageinfo_list_widget.setSelectionMode(QListWidget.SingleSelection)
        self.searched_imageinfo_list_widget.keyPressEvent = self._search_keypress_event
        # 리스트 위젯을 레이아웃에 추가합니다.
        list_widget_layout.addWidget(self.searched_imageinfo_list_widget)

        # 우측 이미지 리스트 설정
        self.selected_imageinfo_list_widget = QListWidget()
        self.selected_imageinfo_list_widget.currentItemChanged.connect(self._emit_current_item_changed)
        self.selected_imageinfo_list_widget.itemClicked.connect(self._emit_current_item_changed)
        self.selected_imageinfo_list_widget.alternatingRowColors()
        self.selected_imageinfo_list_widget.setSelectionMode(QListWidget.SingleSelection)
        self.selected_imageinfo_list_widget.keyPressEvent = self._select_keypress_event
        # 리스트 위젯을 레이아웃에 추가합니다.
        list_widget_layout.addWidget(self.selected_imageinfo_list_widget)

        label_layout = QHBoxLayout()
        self.delete_searched_button = QPushButton('휴지통으로')
        self.delete_searched_button.clicked.connect(self._on_delete_searched_button_clicked)
        self.delete_searched_button.setDisabled(True)
        self.searched_images_count_label = QLabel('검색된 이미지 수: 0')
        self.searched_images_count_label.setAlignment(Qt.AlignRight)
        self.searched_images_count_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        left_layout = QHBoxLayout()
        left_layout.addWidget(self.delete_searched_button)
        left_layout.addWidget(self.searched_images_count_label)
        self.selected_images_count_label = QLabel('선택된 이미지 수: 0')
        self.selected_images_count_label.setAlignment(Qt.AlignRight)
        self.selected_images_count_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        right_layout = QHBoxLayout()
        right_layout.addWidget(self.selected_images_count_label)
        label_layout.addLayout(left_layout, 5)
        label_layout.addLayout(right_layout, 5)

        self.layout.addLayout(label_layout)
        self.layout.addLayout(list_widget_layout)

    def update_searched_list_widget(self, image_infos: list[ImageFileInfo]) -> None:
        if len(image_infos) == 0:
            self.delete_searched_button.setDisabled(True)
            return
        self.searched_imageinfo_list_widget.clear()
        for image_info in image_infos:
            item = QListWidgetItem()
            item.setText(f"{image_info.file_name}")
            item.setData(Qt.UserRole, image_info)
            self.searched_imageinfo_list_widget.addItem(item)
        self.searched_imageinfo_list_widget.sortItems(order=Qt.AscendingOrder)
        self.searched_imageinfo_list_widget.scrollToTop()
        self.searched_images_count_label.setText(f'검색된 이미지 수: {len(image_infos)}')
        self.delete_searched_button.setDisabled(False)
        self.searched_imageinfo_list_widget.setFocus()
        self.searched_imageinfo_list_widget.setCurrentRow(0)

    def get_selected_imageinfos(self) -> set[ImageFileInfo]:
        result: set[ImageFileInfo] = set()
        for index in range(self.selected_imageinfo_list_widget.count()):
            item = self.selected_imageinfo_list_widget.item(index)
            image_info: ImageFileInfo = item.data(Qt.UserRole)
            result.add(image_info)
        return result
    
    def get_searched_imageinfos(self) -> set[ImageFileInfo]:
        result: set[ImageFileInfo] = set()
        for index in range(self.searched_imageinfo_list_widget.count()):
            item = self.searched_imageinfo_list_widget.item(index)
            image_info: ImageFileInfo = item.data(Qt.UserRole)
            result.add(image_info)
        return result

    def clear(self):
        self.searched_imageinfo_list_widget.clear()
        self.selected_imageinfo_list_widget.clear()
        self.searched_images_count_label.setText('검색된 이미지 수: 0')
        self.selected_images_count_label.setText('선택된 이미지 수: 0')
        self._on_selected_list_changed(True)

    def search_list_clear(self):
        self.searched_imageinfo_list_widget.clear()
        self.delete_searched_button.setDisabled(True)
        self.searched_images_count_label.setText('검색된 이미지 수: 0')

    ##########################################
    #          Private Methods               #
    ##########################################

    def _emit_current_item_changed(self):
        sender_widget: QListWidget = self.sender()
        if sender_widget.currentItem() is None:
            return
        current_item_info = sender_widget.currentItem().data(Qt.UserRole)
        self.on_selected_image_changed.emit(current_item_info)

    def _search_keypress_event(self, event):
        """
        검색리스트 위젯의 키 이벤트
        """
        if event.key() == Qt.Key_Delete:
            self._delete_item(self.searched_imageinfo_list_widget, self.searched_imageinfo_list_widget.currentItem())
        elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier:
            self._undo_task()
        elif event.key() == Qt.Key_Right:
            if event.modifiers() & Qt.ControlModifier:
                self.selected_imageinfo_list_widget.setFocus()
                if self.selected_imageinfo_list_widget.currentItem() is None:
                    self.selected_imageinfo_list_widget.setCurrentRow(0)
            elif self.searched_imageinfo_list_widget.currentItem() is not None:
                self._move_item(self.searched_imageinfo_list_widget, self.selected_imageinfo_list_widget, self.searched_imageinfo_list_widget.currentItem())
        else:
            QListWidget.keyPressEvent(self.searched_imageinfo_list_widget, event)

    def _select_keypress_event(self, event):
        """
        선택리스트 위젯의 키 이벤트
        """
        if event.key() == Qt.Key_Delete:
            self._delete_item(self.selected_imageinfo_list_widget, self.selected_imageinfo_list_widget.currentItem())
        elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier:
            self._undo_task()
        elif event.key() == Qt.Key_Left:
            if event.modifiers() & Qt.ControlModifier:
                self.searched_imageinfo_list_widget.setFocus()
            elif self.selected_imageinfo_list_widget.currentItem() is not None:
                self._move_item(self.selected_imageinfo_list_widget, self.searched_imageinfo_list_widget, self.selected_imageinfo_list_widget.currentItem())

        else:
            QListWidget.keyPressEvent(self.selected_imageinfo_list_widget, event)

    def _move_item(self, source_list_widget : QListWidget, destination_list_widget : QListWidget, item : QListWidgetItem):
        # 아이템 이동 로직
        target_index = source_list_widget.row(item)
        target_item = source_list_widget.takeItem(target_index)
        destination_list_widget.addItem(target_item)
        # 이동 이력 저장
        CRhistoryManager.add_move_history(source_list_widget, destination_list_widget, target_item, target_index) 
        self._update_count_label()

    def _delete_item(self, source_list_widget: QListWidget, target_item: QListWidgetItem):
        self.on_user_delete_item.emit()
        delete_index: int = source_list_widget.row(target_item)
        deleted_item = source_list_widget.takeItem(delete_index)
        CRhistoryManager.add_delete_history(source_list_widget, deleted_item, delete_index)
        self._update_count_label()

    def _on_delete_searched_button_clicked(self):
        # 검색된 이미지 리스트의 모든 아이템을 삭제
        if self.searched_imageinfo_list_widget.count() < 0:
            return
        searched_images = self.get_searched_imageinfos()
        FileManager.delete_files(searched_images)
        DataContainer.delete_loaded_image_infos(searched_images)
        self.on_deleted_search_list.emit(f"{len(searched_images)}개의 이미지가 삭제되었습니다.")
        self.searched_imageinfo_list_widget.clear()
        self.delete_searched_button.setDisabled(True)

    def _undo_task(self):
        CRhistoryManager.undo()
        self._update_count_label()

    def _update_count_label(self):
        self.search_count = self.searched_imageinfo_list_widget.count()
        self.selected_count = self.selected_imageinfo_list_widget.count()
        self.searched_images_count_label.setText(f'검색된 이미지 수: {self.search_count}')
        self.selected_images_count_label.setText(f'선택된 이미지 수: {self.selected_count}')
        if self.selected_count > 0:
            self._on_selected_list_changed(False)
        else:
            self._on_selected_list_changed(True)

    def _on_selected_list_changed(self, is_empty: bool):
        self.on_selected_list_changed.emit(is_empty)

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
    on_clicked_option_button = pyqtSignal()
    on_clicked_move_files_button = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.path_label = QLabel('선택된 경로 없음 ( 이미지가 존재하는 폴더를 선택하세요. )')
        self.layout.addWidget(self.path_label, 7)  # 비율 설정

        button_layout = QHBoxLayout()
        path_button = QPushButton('경로 선택')
        path_button.clicked.connect(self.choose_path)
        self.option_button = QPushButton('옵션')
        self.option_button.clicked.connect(self.emit_option_button_clicked)
        self.move_files_button = QPushButton('결과 저장')
        self.move_files_button.setToolTip('검색된 이미지를 모아 폴더를 생성합니다. (기본 폴더 이름: 검색키워드_..._Copy/Move)')
        self.move_files_button.clicked.connect(self.emit_move_files_button_clicked)
        self.move_files_button.setDisabled(True)

        button_layout.addWidget(path_button)
        button_layout.addWidget(self.option_button)
        button_layout.addWidget(self.move_files_button)

        self.layout.addLayout(button_layout)
        self.count_label = QLabel('로드된 이미지 수: 0')
        self.layout.addWidget(self.count_label, 1)

    def update_move_button_status(self, is_enable: bool):
        self.move_files_button.setDisabled(is_enable)

    def choose_path(self):
        selected_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if selected_path:
            self.on_path_selected.emit(selected_path)

    def set_path_label(self, path: str):
        self.path_label.setText(path)

    def update_count_label(self, count: int):
        self.count_label.setText(f'로드된 이미지 수: {count}')

    def emit_option_button_clicked(self):
        self.on_clicked_option_button.emit()

    def emit_move_files_button_clicked(self):
        self.on_clicked_move_files_button.emit()

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

        button_layout = QHBoxLayout()

        self.ok_button = QPushButton("확인")
        self.ok_button.clicked.connect(self.accept)

        self.open_folder_button = QPushButton("폴더 열기")
        self.open_folder_button.clicked.connect(self.open_folder)
        self.open_folder_button.clicked.connect(self.accept)
        self.target_folder_path = None
        self.open_folder_button.hide()

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.open_folder_button)
        self.layout.addWidget(self.label)
        self.layout.addLayout(button_layout)

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

    @staticmethod
    def show_with_folder_open_button(message: str, folder_path: str, parent=None):
        if parent == None:
            parent = CRPopupWindow.parent
        popup = CRPopupWindow(parent)
        popup.open_folder_button.show()
        popup.label.setText(message)
        popup.target_folder_path = folder_path
        print(f"{folder_path}에 저장되었습니다.")
        popup.setFixedSize(popup.sizeHint().width(), popup.sizeHint().height())
        winsound.PlaySound("SystemAsterisk", winsound.SND_ASYNC | winsound.SND_ALIAS)
        popup.exec()

    def set_type(self, popup_type: int):
        type_text = CRPopupWindow._popup_title.get(popup_type, "알림")
        self.setWindowTitle(type_text)

    @staticmethod
    def set_main_window(main_window):
        CRPopupWindow.parent = main_window

    def open_folder(self):
        if self.target_folder_path:
            os.startfile(self.target_folder_path)