__version__ = '0.01'
import sys
from PyQt6.QtCore import *
from PyQt6.QtWidgets import QTableWidget, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QTableWidgetItem
from PyQt6.QtWidgets import QSpacerItem, QSizePolicy
from PyQt6.QtWidgets import QApplication
from trbase.std.trtable import TrTable
from trbase.pyqtwidgets.helper import trtable_to_qttablewidget
from trbase.pyqtwidgets.editlistwidget.editlistwidget import QEditListDialog


class QEditTableWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.table = TrTable([], [])

        # edit buttons
        self.edit_header_button = QPushButton(self)
        self.add_row_button = QPushButton(self)
        self.rem_row_button = QPushButton(self)
        self.up_row_button = QPushButton(self)
        self.down_row_button = QPushButton(self)
        self.save_button = QPushButton(self)
        self.set_button_texts()
        self.add_button_tooltip()
        self.set_button_widths()

        # combine buttons in layout
        self.button_layout = QVBoxLayout()
        self.button_layout.setSpacing(0)
        self.button_layout.addWidget(self.edit_header_button)
        self.button_layout.addWidget(self.add_row_button)
        self.button_layout.addWidget(self.rem_row_button)
        self.button_layout.addWidget(self.up_row_button)
        self.button_layout.addWidget(self.down_row_button)
        self.vertical_button_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.button_layout.addItem(self.vertical_button_spacer)
        self.button_layout.addWidget(self.save_button)

        # list widget
        self.table_widget = QTableWidget()

        # combine list widget and button layout
        self.combine_layout = QHBoxLayout()
        self.combine_layout.setSpacing(0)
        self.combine_layout.addWidget(self.table_widget)
        self.combine_layout.addLayout(self.button_layout)

        # set central layout and connect functions
        self.layout.addLayout(self.combine_layout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.connect()

    def set_button_texts(self, edit: str = 'Edit', add: str = 'Add', rem: str = 'Rem', up: str = "Up", dn: str = 'Dn'):
        self.edit_header_button.setText(edit)
        self.add_row_button.setText(add)
        self.rem_row_button.setText(rem)
        self.up_row_button.setText(up)
        self.up_row_button.setEnabled(False)
        self.down_row_button.setText(dn)
        self.down_row_button.setEnabled(False)
        self.save_button.setText('Upd')

    def add_button_tooltip(self):
        self.edit_header_button.setToolTip('Edit Header')
        self.add_row_button.setToolTip('Add row to table')
        self.rem_row_button.setToolTip('Remove current row from table')
        self.up_row_button.setToolTip('Move current row up')
        self.down_row_button.setToolTip('Move current row down')
        self.save_button.setToolTip('Save Table')

    def set_button_widths(self, edit: int = 35, add: int = 35, rem: int = 35, up: int = 35, dn: int = 35,
                          save: int = 35):
        self.edit_header_button.setFixedWidth(edit)
        self.add_row_button.setFixedWidth(add)
        self.rem_row_button.setFixedWidth(rem)
        self.up_row_button.setFixedWidth(up)
        self.down_row_button.setFixedWidth(dn)
        self.save_button.setFixedWidth(save)

    # noinspection PyUnresolvedReferences
    def connect(self):
        self.edit_header_button.clicked.connect(self.edit_header)
        self.add_row_button.clicked.connect(self.add_row)
        self.rem_row_button.clicked.connect(self.remove_row)

        self.up_row_button.clicked.connect(self.move_row_up)
        self.down_row_button.clicked.connect(self.move_row_down)

        self.save_button.clicked.connect(self.save)

        # self.table_widget.doubleClicked.connect(self.edit_item)

    def set_table(self, table: TrTable) -> bool:
        if not isinstance(table, TrTable):
            return False
        self.table = table
        self.__update_widget__()
        return True

    def __update_widget__(self):
        trtable_to_qttablewidget(self.table, self.table_widget)

    def __update_table__(self):
        header = [self.table_widget.horizontalHeaderItem(i).text()
                  for i in range(self.table_widget.horizontalHeader().count())]
        data = list()
        for r in range(self.table_widget.rowCount()):
            row = list()
            for c in range(self.table_widget.columnCount()):
                item = self.table_widget.item(r, c)
                row.append(item.text())
            data.append(row)
        self.table = TrTable(header, data)
        self.table.show(True, fit_columns=True)

    def edit_header(self):
        dialog = QEditListDialog(self, 'Edit Header', self.table.header)
        dialog.show()
        dialog.exec()

        if dialog.pressed == 'ok':
            new_header = dialog.list
            old_header = self.table.header
            new_data = []
            for row in self.table.data:
                new_row = [row[old_header.index(h)] if h in old_header else '' for h in new_header]
                new_data.append(new_row)
            self.table = TrTable(new_header, new_data)
            self.__update_widget__()

    def edit_item(self):
        pass

    def add_row(self, item: QTableWidgetItem or str):
        data = self.table.data
        new_row = [''] * len(self.table.header)
        data.append(new_row)
        self.table = TrTable(self.table.header, data)
        self.__update_widget__()

    def remove_row(self):
        row = self.table_widget.currentRow()
        if row < 0:
            return
        data = self.table.data
        data.pop(row)
        self.table = TrTable(self.table.header, data)
        self.__update_widget__()

    def move_row_up(self):
        pass

    def move_row_down(self):
        pass

    def save(self):
        self.__update_table__()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_F2:
            # F2 pressed
            self.edit_item()
        else:
            self.__update_table__()
        return super().keyPressEvent(e)


# TEST ================================================================================================================
class ExampleWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(300, 300)
        self.setWindowTitle("Test Widget")

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        tw = QEditTableWidget(self)
        _header = ['ID', 'Name', 'Description']
        _data = [
            [1, 'First Name', 'This is a first name item'],
            [1, 'Second Name', 'This is a second name item'],
        ]
        table = TrTable(_header, _data)
        tw.set_table(table)
        layout.addWidget(tw)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = ExampleWidget()
    gui.show()
    sys.exit(app.exec())


