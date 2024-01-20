from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QTextCursor, QTextCharFormat
import inspect
import datetime
from dataclasses import dataclass
from icecream import ic


@dataclass()
class ErrorEntry:
    method_name: str
    type: str
    message: str
    timestamp: datetime.datetime = datetime.datetime.now()


class TrQWidget(QWidget):
    def dummy(self):
        try:
            sender = self.sender().objectName()
            self.update_log('Function "{}" not implemented yet'.format(sender))
        except Exception as e:
            self.__error_entry__(inspect.currentframe().f_code.co_name, e)

    @staticmethod
    def update_log(message: str or ErrorEntry):
        # self.emit(SIGNAL("a2l_labels_message"), message)
        ic(message)

    def __error_entry__(self, method_name: str, e: Exception):
        error_entry = ErrorEntry(method_name, type(e).__name__, str(e))
        self.update_log(error_entry)

    @staticmethod
    def reset_text_edit(handle):
        handle.clear()
        # font = QFont()
        # font.setBold(False)
        # font.setItalic(False)
        # font.setStrikeOut(False)
        # font.setFamily('Ubuntu Mono')
        # cursor = handle.textCursor()
        # cursor.setPosition(0)
        # handle.setFont(font)

        cursor = handle.textCursor()
        cursor.select(QTextCursor.document)
        cursor.setCharFormat(QTextCharFormat())
        cursor.clearSelection()
        handle.setTextCursor(cursor)

    def connect(self):
        try:
            pass
        except Exception as e:
            self.__error_entry__(inspect.currentframe().f_code.co_name, e)
