import sys
from maingui import MainGUI
from CreeperGUI import CRPopupWindow

from PyQt5.QtWidgets import QApplication

def run():
    app = QApplication(sys.argv)
    main_gui = MainGUI()
    CRPopupWindow.set_main_window(main_gui)
    main_gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run()

# Pyinstaller로 실행파일 만들기
# pyinstaller --onefile --icon=Icon.ico --add-data "Icon.ico:." -n ImageCreeper run.py
# or
# pyinstaller --onefile --icon=Icon.ico --add-data --noconsole "Icon.ico:." -n ImageCreeper run.py 