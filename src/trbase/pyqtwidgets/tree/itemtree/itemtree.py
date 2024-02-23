import sys
from typing import List
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTreeWidget, QMenu, QTreeWidgetItem, QInputDialog, QLineEdit
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String, Integer
from sqlalchemy.orm import Session
from sqlalchemy import select
from trbase.pyqtwidgets.helper import add_parent_to_qttreewidget


class Base(DeclarativeBase):
    pass


class TrItemTreeItem(Base):
    __tablename__ = "trtreeitems"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    parent_id: Mapped[int] = mapped_column(Integer)
    level: Mapped[int]
    position: Mapped[int]
    expanded: Mapped[bool]

    def __repr__(self) -> str:
        return (f"TrItemTreeItem(id={self.id!r}, name={self.name!r}, parent_id={self.parent_id!r} " +
                f"level={self.level!r}, position={self.position!r}, expanded={self.expanded!r})")


class TrItemTreeWidget(QTreeWidget):
    def __init__(self, parent=None, sqlite_file_name: str = 'trtreeitemwidget'):
        super().__init__(parent)
        self.header().hide()
        self.engine = create_engine(r'sqlite:///./{}.sqlite'.format(sqlite_file_name), echo=False)
        self.context_menu = self.get_context_menu()

        # noinspection PyUnresolvedReferences
        self.itemDoubleClicked.connect(self.edit_item_name)

        self.__init_database_table__()
        self.connect_triggers()
        self.show_items()

    def __init_database_table__(self):
        Base.metadata.create_all(self.engine)

    def contextMenuEvent(self, event):
        # Show the context menu
        self.context_menu.exec(self.mapToGlobal(event.pos()))

    def get_context_menu(self) -> QMenu:
        selected_text = 'DUMMY NAME'

        # create menuD
        menu = QMenu()

        action_add_item = menu.addAction("Add item")
        self.__add_action_trigger__(action_add_item, self.add_item)
        action_remove_item = menu.addAction("Remove item")
        self.__add_action_trigger__(action_remove_item, self.remove_item)

        # action_add_child_item = menu.addAction("Add child item")
        # self.__add_action_trigger__(action_add_child_item, self.add_child_item)

        action_move_up = menu.addAction("Move up")
        self.__add_action_trigger__(action_move_up, self.move_item_up)
        action_move_down = menu.addAction("Move down")
        self.__add_action_trigger__(action_move_down, self.move_item_down)
        action_indent_item = menu.addAction("Indent item")
        self.__add_action_trigger__(action_indent_item, self.indent_item)
        action_outdent_item = menu.addAction("Outdent item")
        self.__add_action_trigger__(action_outdent_item, self.outdent_item)

        return menu

    @staticmethod
    def __add_action_trigger__(action: QAction, fun):
        """ helper function for adding context menu functions to action"""
        # noinspection PyUnresolvedReferences
        action.triggered.connect(fun)

    def connect_triggers(self):
        # noinspection PyUnresolvedReferences
        self.itemExpanded.connect(self.update_item_expanded)
        # noinspection PyUnresolvedReferences
        self.itemCollapsed.connect(self.update_item_expanded)

    def disconnect_triggers(self):
        # noinspection PyUnresolvedReferences
        self.itemExpanded.disconnect(self.update_item_expanded)
        # noinspection PyUnresolvedReferences
        self.itemCollapsed.disconnect(self.update_item_expanded)

    def get_current_item(self) -> (TrItemTreeItem or None, QTreeWidgetItem):
        ci = self.currentItem()
        ci = ci if self.selectedItems() else None
        data = ci.data(0, Qt.ItemDataRole.UserRole) if ci is not None else None
        return data, ci

    def show_items(self):
        self.clear()
        self.disconnect_triggers()
        with Session(self.engine) as session:
            stmt = select(TrItemTreeItem).order_by(TrItemTreeItem.position).where(TrItemTreeItem.parent_id.is_(-1))
            items = [item for item in session.scalars(stmt)]
            self.__add_tree_children__(session=session, root=self.invisibleRootItem(), items=items)
        self.connect_triggers()

    def __add_tree_children__(self, session, root: QTreeWidgetItem, items: List[TrItemTreeItem]):
        for item in items:
            node = add_parent_to_qttreewidget(parent=root, column=0, title=item.name, data=item, expanded=item.expanded)
            stmt = select(TrItemTreeItem).order_by(TrItemTreeItem.position).where(TrItemTreeItem.parent_id.is_(item.id))
            children = [item for item in session.scalars(stmt)]
            if children:
                self.__add_tree_children__(session=session, root=node, items=children)

    def __get_all_children__(self, session, item_ids: List[int]) -> List[int]:
        ids = list()
        for item_id in item_ids:
            stmt = select(TrItemTreeItem).where(TrItemTreeItem.parent_id.is_(item_id))
            child_items = [item.id for item in session.scalars(stmt)]
            for child_item in child_items:
                ids.append(child_item)
                ids += self.__get_all_children__(session, [child_item])
        return ids

    def add_item(self, dkn: bool, name: str = 'New Item'):
        parent_item, _ = self.get_current_item()
        with Session(self.engine) as session:
            if parent_item is not None:
                stmt = select(TrItemTreeItem).where(TrItemTreeItem.parent_id.is_(parent_item.id))
            else:
                stmt = select(TrItemTreeItem).where(TrItemTreeItem.parent_id.is_(-1))
            items = [item for item in session.scalars(stmt)]
        new_pos = max([item.position for item in items]) + 1 if items else 0
        new_item = TrItemTreeItem(
            name=name,
            parent_id=parent_item.id if parent_item is not None else -1,
            level=parent_item.level + 1 if parent_item is not None else 0,
            position=new_pos,
            expanded=True,
        )
        with Session(self.engine) as session:
            session.add_all([new_item])
            session.commit()
        self.show_items()

    def edit_item_name(self, node: QTreeWidgetItem):
        text, ok = QInputDialog.getText(self, 'Edit Item', 'Name:', text=node.text(0))
        if ok:
            data = node.data(0, Qt.ItemDataRole.UserRole)
            with Session(self.engine) as session:
                stmt = select(TrItemTreeItem).where(TrItemTreeItem.id == data.id)
                item = session.scalars(stmt).one()
                item.name = text
                session.commit()
            node.setText(0, text)
            node.setExpanded(True)

    def update_item_expanded(self, node: QTreeWidgetItem):
        data = node.data(0, Qt.ItemDataRole.UserRole)
        with Session(self.engine) as session:
            stmt = select(TrItemTreeItem).where(TrItemTreeItem.id == data.id)
            item = session.scalars(stmt).one()
            item.expanded = node.isExpanded()
            session.commit()

    def remove_item(self):
        item, _ = self.get_current_item()
        if item is None:
            return
        with Session(self.engine) as session:
            remove_ids = self.__get_all_children__(session, [item.id])
            remove_ids.append(item.id)
            stmt = select(TrItemTreeItem).where(TrItemTreeItem.id.in_(remove_ids))
            items = [item for item in session.scalars(stmt)]
            for item in items:
                print('delete: {}'.format(item))
                session.delete(item)
            session.commit()
        self.show_items()

    def add_child_item(self):
        pass

    def move_item_up(self):
        item, node = self.get_current_item()
        if node is None:
            return
        if item.position == 0:
            return
        parent_node = node.parent()
        parent_item = parent_node.data(0, Qt.ItemDataRole.UserRole) if parent_node is not None else None
        parent_id = parent_item.id if parent_item is not None else -1
        with Session(self.engine) as session:
            stmt1 = select(TrItemTreeItem).where(
                (TrItemTreeItem.id.is_(item.id) &
                 TrItemTreeItem.parent_id.is_(parent_id))
            )
            select_item = session.scalars(stmt1).one()

            stmt2 = select(TrItemTreeItem).where(
                (TrItemTreeItem.position.is_(item.position - 1) &
                 TrItemTreeItem.parent_id.is_(parent_id) &
                 TrItemTreeItem.level.is_(item.level))
            )
            select_above_item = session.scalars(stmt2).one()

            select_item.position -= 1
            select_above_item.position += 1
            session.commit()
        self.show_items()

    def move_item_down(self):
        item, node = self.get_current_item()
        if node is None:
            return
        parent_node = node.parent()
        parent_item = parent_node.data(0, Qt.ItemDataRole.UserRole) if parent_node is not None else None
        parent_id = parent_item.id if parent_item is not None else -1
        with Session(self.engine) as session:
            stmt1 = select(TrItemTreeItem.position).where(
                (TrItemTreeItem.level.is_(item.level) & TrItemTreeItem.parent_id.is_(parent_id))
            )
            positions = [i for i in session.scalars(stmt1)]
        if item.position == max(positions):
            return
        with Session(self.engine) as session:
            stmt1 = select(TrItemTreeItem).where(
                (TrItemTreeItem.id.is_(item.id) &
                 TrItemTreeItem.parent_id.is_(parent_id))
            )
            select_item = session.scalars(stmt1).one()

            stmt2 = select(TrItemTreeItem).where(
                (TrItemTreeItem.position.is_(item.position + 1) &
                 TrItemTreeItem.parent_id.is_(parent_id) &
                 TrItemTreeItem.level.is_(item.level))
            )
            select_below_item = session.scalars(stmt2).one()

            select_item.position += 1
            select_below_item.position -= 1
            session.commit()
        self.show_items()

    def indent_item(self):
        item, node = self.get_current_item()
        if node is None:
            return
        if item.position == 0:
            return
        parent_node = node.parent()
        parent_item = parent_node.data(0, Qt.ItemDataRole.UserRole) if parent_node is not None else None
        parent_id = parent_item.id if parent_item is not None else -1
        with Session(self.engine) as session:
            stmt1 = select(TrItemTreeItem).where(
                (TrItemTreeItem.id.is_(item.id) &
                 TrItemTreeItem.parent_id.is_(parent_id))
            )
            select_item = session.scalars(stmt1).one()

            stmt2 = select(TrItemTreeItem).where(
                (TrItemTreeItem.position.is_(item.position - 1) &
                 TrItemTreeItem.parent_id.is_(parent_id) &
                 TrItemTreeItem.level.is_(item.level))
            )
            select_above_item = session.scalars(stmt2).one()
            stmt3 = select(TrItemTreeItem).where(TrItemTreeItem.parent_id.is_(select_above_item.id))
            children_positions = [i.position for i in session.scalars(stmt3)]

            select_item.level += 1
            select_item.parent_id = select_above_item.id
            select_item.position = max(children_positions) + 1 if children_positions else 0
            session.commit()
        self.show_items()

    def outdent_item(self):
        item, node = self.get_current_item()
        if node is None:
            return
        if item.level == 0:
            return
        parent_node = node.parent()
        parent_item = parent_node.data(0, Qt.ItemDataRole.UserRole) if parent_node is not None else None
        parent_id = parent_item.id if parent_item is not None else -1
        with Session(self.engine) as session:
            stmt1 = select(TrItemTreeItem).where(
                (TrItemTreeItem.id.is_(item.id) &
                 TrItemTreeItem.parent_id.is_(parent_id))
            )
            select_item = session.scalars(stmt1).one()

            stmt2 = select(TrItemTreeItem).where(TrItemTreeItem.parent_id.is_(parent_item.parent_id))
            children_positions = [i.position for i in session.scalars(stmt2)]

            select_item.level -= 1
            select_item.parent_id = parent_item.parent_id
            select_item.position = max(children_positions) + 1 if children_positions else 0
            session.commit()
        self.show_items()


# TEST ===============================================================================================================
class ExampleWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(300, 300)
        self.setWindowTitle("TreeItem Widget")

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        lw = TrItemTreeWidget(self)
        # lw.add_item(False, name='TEST 1')
        layout.addWidget(lw)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = ExampleWidget()
    gui.show()
    sys.exit(app.exec())


if __name__ == '__main__':

    tt = TrItemTreeWidget()
