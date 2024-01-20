__version__ = '0.01'
import sys
from PyQt6.QtCore import *
from PyQt6.QtWidgets import QListWidget, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QListWidgetItem, QDialog
from PyQt6.QtWidgets import QSpacerItem, QSizePolicy
from PyQt6.QtWidgets import QApplication


class QEditListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.list = list()
        self.layout = QVBoxLayout(self)

        # edit buttons
        self.add_button = QPushButton(self)
        self.rem_button = QPushButton(self)
        self.up_button = QPushButton(self)
        self.down_button = QPushButton(self)
        self.set_button_texts()
        self.set_button_widths()

        # combine buttons in layout
        self.button_layout = QVBoxLayout()
        self.button_layout.setSpacing(0)
        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.rem_button)
        self.button_layout.addWidget(self.up_button)
        self.button_layout.addWidget(self.down_button)
        self.vertical_button_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.button_layout.addItem(self.vertical_button_spacer)

        # list widget
        self.list_widget = QListWidget()

        # combine list widget and button layout
        self.combine_layout = QHBoxLayout()
        self.combine_layout.setSpacing(0)
        self.combine_layout.addWidget(self.list_widget)
        self.combine_layout.addLayout(self.button_layout)

        # set central layout and connect functions
        self.layout.addLayout(self.combine_layout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.connect()

    def set_button_texts(self, add: str = 'Add', rem: str = 'Rem', up: str = "Up", dn: str = 'Dn'):
        self.add_button.setText(add)
        self.rem_button.setText(rem)
        self.up_button.setText(up)
        self.down_button.setText(dn)

    def set_button_widths(self, add: int = 35, rem: int = 35, up: int = 35, dn: int = 35):
        self.add_button.setFixedWidth(add)
        self.rem_button.setFixedWidth(rem)
        self.up_button.setFixedWidth(up)
        self.down_button.setFixedWidth(dn)

    # noinspection PyUnresolvedReferences
    def connect(self):
        self.list_widget.doubleClicked.connect(self.edit_item)
        self.add_button.clicked.connect(self.add_item)
        self.rem_button.clicked.connect(self.remove_item)

        self.up_button.clicked.connect(self.move_up)
        self.down_button.clicked.connect(self.move_down)

    def set_list(self, value: list) -> bool:
        if not isinstance(value, list):
            return False
        self.list = value
        self.__update_widget__()
        return True

    def __update_widget__(self):
        for name in self.list:
            item = QListWidgetItem()
            item.setText(name)
            self.list_widget.addItem(item)

    def __update_list__(self):
        self.list = list()
        for i in range(self.list_widget.count()):
            list_widget_item = self.list_widget.item(i)
            self.list.append(list_widget_item.text())

    def edit_item(self):
        item = self.list_widget.currentItem()
        self.list_widget.openPersistentEditor(item)
        self.__update_list__()

    def add_item(self, item: QListWidgetItem or str):
        if not (isinstance(item, QListWidgetItem) or isinstance(item, str)):
            item = QListWidgetItem()
            item.setText('New Item')
            # item.setFlags(Qt.ItemIsEditable)
        self.list_widget.addItem(item)
        self.__update_list__()

    def remove_item(self):
        item = self.list_widget.currentItem()
        if not item:
            return
        self.list_widget.takeItem(self.list_widget.row(item))
        self.close_persistent_editor()
        self.__update_list__()

    def move_up(self):
        row = self.list_widget.currentRow()
        if row <= 0:
            return
        item = self.list_widget.takeItem(row)
        new_row = row - 1
        self.list_widget.insertItem(new_row, item)
        self.list_widget.setCurrentRow(new_row)
        self.__update_list__()

    def move_down(self):
        row = self.list_widget.currentRow()
        if row < 0:
            return
        if row > self.list_widget.count():
            return
        item = self.list_widget.takeItem(row)
        new_row = row + 1
        self.list_widget.insertItem(new_row, item)
        self.list_widget.setCurrentRow(new_row)
        self.__update_list__()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Return:
            # enter pressed
            self.close_persistent_editor()
        elif e.key() == 16777235 or e.key() == 16777237:
            # up, dow key pressed
            self.close_persistent_editor()
            return super().keyPressEvent(e)
        elif e.key() == Qt.Key.Key_F2:
            # F2 pressed
            self.edit_item()
        return super().keyPressEvent(e)

    def close_persistent_editor(self):  # Check if user are editing item
        item = self.list_widget.currentItem()
        if not item:
            return
        if self.list_widget.isPersistentEditorOpen(item):
            self.list_widget.closePersistentEditor(item)
        self.__update_list__()


class QEditListDialog(QDialog):
    def __init__(self, parent=None, title: str = 'Edit List Dialog', start_list=None):
        super().__init__(parent)
        if start_list is None:
            start_list = list()
        self.resize(300, 300)
        self.setWindowTitle(title)
        self.list = start_list

        # main layout
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # list widget
        self.__lw__ = QEditListWidget(self)
        self.__lw__.set_list(self.list)
        layout.addWidget(self.__lw__)

        # OK and cancel buttons
        self.pb_ok = QPushButton(self)
        self.pb_ok.setText('OK')
        # noinspection PyUnresolvedReferences
        self.pb_ok.clicked.connect(self.ok_clicked)
        self.pb_cancel = QPushButton(self)
        self.pb_cancel.setText('Cancel')
        # noinspection PyUnresolvedReferences
        self.pb_cancel.clicked.connect(self.cancel_clicked)

        hl = QHBoxLayout()
        hl.addWidget(self.pb_ok)
        hl.addWidget(self.pb_cancel)
        layout.addLayout(hl)

        self.pressed = 'cancel'

    def ok_clicked(self):
        self.pressed = 'ok'
        self.list = list()
        for i in range(self.__lw__.list_widget.count()):
            list_widget_item = self.__lw__.list_widget.item(i)
            self.list.append(list_widget_item.text())
        self.close()

    def cancel_clicked(self):
        self.close()


# TEST ================================================================================================================
class ExampleWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(300, 300)
        self.setWindowTitle("List Edit Widget")

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        lw = QEditListWidget(self)
        lw.set_list(['Horst', 'Remse'])
        layout.addWidget(lw)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = ExampleWidget()
    gui.show()
    sys.exit(app.exec())


