from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QAbstractItemView, QMenu, QTreeView
from trbase.pyqtwidgets.tree.trtreemodel import TrTreeItem


class ReBaseTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # noinspection PyUnresolvedReferences
        self.customContextMenuRequested.connect(self.contextMenuEvent)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    def contextMenuEvent(self, pos):
        index = self.indexAt(pos)
        if not index.isValid():
            return
        menu = QMenu()
        menu.addAction("Add Child")
        menu.addAction("Remove Item")
        menu.addAction("Edit Item")
        selected_action = menu.exec(self.mapToGlobal(pos))
        if not selected_action:
            return
        value = menu.actions().index(selected_action)
        if value == 0:
            self.add_child(index)
        elif value == 1:
            self.remove_item(index)
        elif value == 2:
            self.edit_item(index)
        else:
            pass

    def model(self):
        return super().model()

    def setModel(self, model):
        super().setModel(model)

    def add_child(self, index):
        model = self.model()
        model.itemFromIndex(index).append_child(
            TrTreeItem(["New Item"], model.itemFromIndex(index))
        )
        self.expandAll()

    def remove_item(self, index):
        model = self.model()
        model.removeRow(index.row(), index.parent())

    def edit_item(self, index):
        self.edit(index)
