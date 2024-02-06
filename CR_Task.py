from abc import ABC, abstractmethod
from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from collections import deque

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
    _undo_history: deque[CRTaskData] = deque(maxlen=10)

    @classmethod
    def add_history(cls, task: CRTaskData):
        if len(cls._undo_history) == cls._undo_history.maxlen:
            cls._undo_history.popleft()
        
        cls._undo_history.append(task)
        print(f"{task} 추가됨. 현재 이력: {len(cls._undo_history)}개")
        for i in cls._undo_history:
            print(i)

    @classmethod
    def add_delete_history(cls, source: QListWidget, item: QListWidgetItem):
        cls.add_history(CRdeleteTask(source, item))

    @classmethod
    def add_move_history(cls, source: QListWidget, destination: QListWidget, item: QListWidgetItem, source_index: int):
        cls.add_history(CRmoveTask(source, destination, item, source_index))

    @classmethod
    def undo(cls):
        if cls._undo_history:
            undo_data: CRTaskData = cls._undo_history.pop()
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