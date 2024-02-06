"""
상수 모음
"""
IMAGE_FORMAT = ('.png')
PROGRAM_NAME = "ImageCreeper"
PROGRAM_VERSION = "v0.1.0"
MAX_FILE_NAME_LENGTH = 50
GUI_STYLE_SHEET = """
            QWidget{
                background-color: #333;
                color: #FFF;
            }
            QLineEdit{
                border-radius: 5px;
                background-color: #444;
                padding: 5px;
                margin: 0px;
            }
            QListWidget, QLabel {
                border-radius: 5px;
                background-color: #444;
                padding: 5px;
                margin: 0px;
            }
            QPushButton {
                border-radius: 10px;
                padding: 6px;
                background-color: #555;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #666;
            }
            QPushButton:pressed {
                background-color: #333;
            }
            QPushButton:disabled {
                background-color: #222;
                text-decoration: line-through;
            }
        """