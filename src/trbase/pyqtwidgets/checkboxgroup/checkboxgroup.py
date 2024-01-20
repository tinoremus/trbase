__version__ = '0.01'
import sys
from PyQt6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox
from PyQt6.QtWidgets import QApplication
from dataclasses import dataclass
from typing import List


@dataclass()
class ConfigItem:
    name: str
    state: bool


@dataclass()
class ConfigList:
    items: list


class QCheckBoxGroup(QWidget):
    def __init__(self, parent: any, config: ConfigList, rows: int = 1, columns: int = 1):
        super().__init__(parent)

        self.config: ConfigList = config
        self.rows: int = rows
        self.columns: int = columns

        self.grid = QGridLayout(self)
        self.grid.setSpacing(0)
        self.grid.setHorizontalSpacing(6)

        i = 0
        for row in range(self.rows):
            for col in range(self.columns):
                if i >= len(self.config.items):
                    continue
                item = self.config.items[i]
                layout, handle = self.__get_item__(item)
                self.grid.addLayout(layout, row, col, 1, 1)
                i += 1
        self.grid.setContentsMargins(0, 0, 0, 0)

    @staticmethod
    def __get_title__(name):
        return name.title().replace('_', ' ')

    def __get_item__(self, item: ConfigItem) -> (QHBoxLayout, QCheckBox):

        horizontal_layout = QHBoxLayout()
        label = QLabel(self.__get_title__(item.name))
        horizontal_layout.addWidget(label)
        handle = QCheckBox()
        handle.setObjectName(item.name)
        handle.setChecked(item.state)
        # noinspection PyUnresolvedReferences
        handle.stateChanged.connect(self.update_check_state)
        horizontal_layout.addWidget(handle)

        return horizontal_layout, handle

    def update_check_state(self, value):
        name = self.sender().objectName()
        items = [item for item in self.config.items if item.name == name]
        item = items[0] if items else None
        if item is None:
            return
        item.state = True if value else False


# TEST ================================================================================================================
class ExampleWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(300, 300)
        self.setWindowTitle("Test Widget")

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        config = ConfigList([
            ConfigItem(name='CPU', state=True),
            ConfigItem(name='GPU', state=True),
            ConfigItem(name='NNAPI', state=True),
        ])
        lw = QCheckBoxGroup(self, config, 2, 3)
        layout.addWidget(lw)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = ExampleWidget()
    gui.show()
    sys.exit(app.exec())


