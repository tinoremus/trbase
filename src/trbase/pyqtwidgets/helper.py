import datetime
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from trbase.std.trtable import TrTable


def trtable_to_qttablewidget(trtable: TrTable, qttablewidget: QTableWidget):
    if trtable.data_rows == 0:
        # empty table
        qttablewidget.setRowCount(0)
        qttablewidget.setColumnCount(0)
        return

    qttablewidget.setRowCount(trtable.data_rows)
    qttablewidget.setColumnCount(trtable.data_columns)

    # HEADER
    if trtable.header_columns > 0:
        qttablewidget.setHorizontalHeaderLabels(trtable.header_single_row)

    # DATA
    for rid, row in enumerate(trtable.data):
        for cid, cell in enumerate(row):
            try:
                if isinstance(cell, datetime.datetime):  # convert datetime to string
                    qttablewidget.setItem(rid, cid, QTableWidgetItem(str(cell)))
                elif isinstance(cell, str):
                    qttablewidget.setItem(rid, cid, QTableWidgetItem(cell))
                elif isinstance(cell, int) or isinstance(cell, int) or isinstance(cell, bool):
                    qttablewidget.setItem(rid, cid, QTableWidgetItem(str(cell)))
                elif isinstance(cell, list):
                    qttablewidget.setItem(rid, cid, QTableWidgetItem('\n'.join(cell)))
                else:
                    qttablewidget.setItem(rid, cid, QTableWidgetItem(str(cell)))
            except Exception as e:
                print(e)
                print(
                    '{}'.format('trtable_to_qttablewidget'),
                    'ERROR', 'Can\'t write item to QTable : {}'.format(cell.__repr__())
                )
                qttablewidget.setItem(rid, cid, QTableWidgetItem("error"))

    # adjust column size to data
    qttablewidget.resizeColumnsToContents()
    qttablewidget.resizeRowsToContents()


def add_parent_to_qttreewidget(
        parent: QTreeWidgetItem, column: int, title: str, data: any, expanded: bool = True, whats_this: str = '',
        check_state: None or Qt.CheckState = None):
    if isinstance(title, list):
        item = QTreeWidgetItem(parent, title)
    else:
        item = QTreeWidgetItem(parent, [title])
    item.setData(column, Qt.ItemDataRole.UserRole, data)
    item.setWhatsThis(column, whats_this)
    item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)
    if check_state is not None:
        item.setCheckState(column, check_state)
    item.setExpanded(expanded)
    return item


def add_child_to_qttreewidget(
        parent: QTreeWidgetItem, column: int, title: str, data: any, whats_this: str = '',
        check_state: Qt.CheckState or None = None):
    if isinstance(title, list) or isinstance(title, tuple):
        item = QTreeWidgetItem(parent, title)
    else:
        item = QTreeWidgetItem(parent, [title])
    item.setData(column, Qt.ItemDataRole.UserRole, data)
    item.setWhatsThis(column, whats_this)
    # item.setFlags(Qt.ItemIsSelectable)
    # item.setFlags(Qt.ItemIsEditable)
    # item.setFlags(Qt.ItemIsDragEnabled)
    # item.setFlags(Qt.ItemIsUserCheckable)
    # item.setFlags(Qt.ItemIsEnabled)
    if check_state is not None:
        item.setCheckState(column, check_state)
    return item


def recursive_check_state_update_parents(child: QTreeWidgetItem) -> bool:
    changed_check_state = False

    # get parent node
    parent = child.parent()
    if parent is None:
        return changed_check_state

    # get selected children
    selected_children_count = 0
    for childID in range(parent.childCount()):
        # update child check state
        if parent.child(childID).checkState(0) > Qt.CheckState.Unchecked:
            selected_children_count += 1

    # print ('{} has selected children count = {}'.format(parent.text(0),selectedChildrenCount))
    # set parent state according to children selection count
    old_check_state = parent.checkState(0)

    if selected_children_count == 0:
        parent.setCheckState(0, Qt.CheckState.Unchecked)
    elif selected_children_count < parent.childCount():
        parent.setCheckState(0, Qt.CheckState.PartiallyChecked)
    elif selected_children_count == parent.childCount():
        parent.setCheckState(0, Qt.CheckState.Checked)

    new_check_state = parent.checkState(0)
    if new_check_state != old_check_state:
        changed_check_state = True

    # call parent's parent
    return_changed_check_state = recursive_check_state_update_parents(parent)
    changed_check_state = changed_check_state or return_changed_check_state

    return changed_check_state


def recursive_check_state_update_children(parent: QTreeWidgetItem) -> bool:
    changed_check_state = False
    # get parent check state
    check_state = parent.checkState(0)
    # set all children checkStates to the same state
    for childID in range(parent.childCount()):

        if check_state != parent.child(childID).checkState(0):
            changed_check_state = True
        # update child check state
        parent.child(childID).setCheckState(0, check_state)
        # call children's children
        return_changed_check_state = recursive_check_state_update_children(parent.child(childID))
        changed_check_state = changed_check_state or return_changed_check_state

    return changed_check_state
