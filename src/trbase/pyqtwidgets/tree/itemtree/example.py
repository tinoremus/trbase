import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from trbase.pyqtwidgets.tree.itemtree.itemtree import TrItemTreeWidget


class ExampleWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(300, 300)
        self.setWindowTitle("TreeItem Widget")

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        lw = TrItemTreeWidget(self)
        layout.addWidget(lw)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = ExampleWidget()
    gui.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    tt = TrItemTreeWidget()
