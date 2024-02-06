from abc import ABC, abstractmethod
from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from queue import LifoQueue

class CRTaskData(ABC):
    """
    undo/redo를 위한 작업 클래스 박싱용 클래스
    """
    @abstractmethod
    def rollback(self):
        pass

class CRhistoryManager():
    """
    undo 관리자
    """
    _undo_history: LifoQueue[CRTaskData] = LifoQueue(maxsize=10)

    @classmethod
    def add_history(cls, task: CRTaskData):
        if not cls._undo_history.full():
            cls._undo_history.put(task)
        else:
            cls._undo_history.get()
            cls._undo_history.put(task)
        print(f"{task}")

    @classmethod
    def add_delete_history(cls, source: QListWidget, item: QListWidgetItem):
        cls.add_history(CRdeleteTask(source, item))

    @classmethod
    def add_move_history(cls, source: QListWidget, destination: QListWidget, item: QListWidgetItem, source_index: int):
        cls.add_history(CRmoveTask(source, destination, item, source_index))

    @classmethod
    def undo(cls):
        if not cls._undo_history.empty():
            undo_data: CRTaskData = cls._undo_history.get()
            undo_data.rollback()
        else:
            print("삭제 이력이 없습니다.")

    @classmethod
    def clear(cls):
        cls._undo_history.queue.clear()

class CRmoveTask(CRTaskData):
    """
    이미지 이동 작업단위
    """
    def __init__(self, source: QListWidget, destination: QListWidget, item: QListWidgetItem, source_index: int):
        self.source = source
        self.source_index = source_index
        self.destination = destination
        self.item = item

    def rollback(self):
        # 아이템을 되돌립니다.
        taked_item = self.destination.takeItem(self.destination.row(self.item))
        self.source.insertItem(self.source_index, taked_item)
        self.source.setFocus()
        self.source.scrollToItem(taked_item)
        self.source.setCurrentItem(taked_item)
        print(f"이동 취소: {taked_item.text()}")

    def __str__(self):
        return f"이동 : {self.item.text()}"

class CRdeleteTask(CRTaskData):
    """
    이미지 삭제 작업단위
    """
    def __init__(self, source: QListWidget, item: QListWidgetItem):
        self.source = source
        self.item_index = source.row(item)
        self.item = item

    def rollback(self):
        self.source.insertItem(self.item_index, self.item)
        self.source.scrollToItem(self.item)
        self.source.setCurrentItem(self.item)
        print(f"삭제 취소: {self.item.text()}")

    def __str__(self):
        return f"삭제 : {self.item.text()}"