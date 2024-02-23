import os
from copy import deepcopy
from PyQt6.QtCore import Qt, QModelIndex
from PyQt6.QtWidgets import QAbstractItemView, QMenu, QTreeView
from PyQt6.QtGui import QAction
from trbase.pyqtwidgets.tree.trtreemodel import TrTreeItem, TrTreeModel
import json
import pickle


class TrStructureTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # noinspection PyUnresolvedReferences
        self.customContextMenuRequested.connect(self.contextMenuEvent)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self._schema_ = list()
        self._flat_ = list()
        self._tree_ = dict()
        self._model_ = None
        self.config_file_path = str()

    @staticmethod
    def get_default_schema() -> list:
        return [
            {'level': 0, 'name': 'Customer', 'object': None},
            {'level': 1, 'name': 'Department', 'object': None},
            {'level': 2, 'name': 'Team', 'object': None},
            {'level': 3, 'name': 'Project', 'object': None},
        ]

    def set_schema(self, schema: list) -> bool:
        if not isinstance(schema, list):
            return False
        self._schema_ = schema
        return True

    def set_config_file_path(self, value: str) -> bool:
        if not isinstance(value, str):
            return False
        self.config_file_path = value
        return True

    def update_all(self):
        self._tree_, self._flat_ = self.get_tree_and_flat_structure()

    def save_config(self):
        self.update_all()
        config = pickle.dumps({
            'schema': self._schema_,
            'tree': self._tree_,
            'flat': self._flat_,
        })
        with open(self.config_file_path, 'wb') as pfile:
            pickle.dump(config, pfile)
        print('Saved all')

    def load_config(self):
        if os.path.exists(self.config_file_path):
            with open(self.config_file_path, 'rb') as pfile:
                tree_dump = pickle.load(pfile)
                config = pickle.loads(tree_dump)
            self._schema_ = config['schema'] if 'schema' in config else list()
            self._tree_ = config['tree'] if 'tree' in config else dict()
            self._flat_ = config['flat'] if 'flat' in config else list()
            self.__load_tree__()
            self.hideColumn(1)
        else:
            self._schema_ = list()
            model = TrTreeModel()
            self.setModel(model)

    def __load_tree__(self):
        model = TrTreeModel()
        self.setModel(model)

        for key in self._tree_:
            # root node
            for sub_key in self._tree_[key]['children']:
                # first actual node
                sub_section = self._tree_[key]['children'][sub_key]
                sub_obj = sub_section['object']
                sub_obj = self.__check_object_updates__(sub_obj)
                sub_item = TrTreeItem([sub_obj.name, sub_obj], None)
                model.appendRow(sub_item)

                sub_row = sub_section['row']
                expanded = sub_section['expanded']
                sub_index = model.index(sub_row, 0, QModelIndex())
                self.setExpanded(sub_index, expanded)

                self.__load_tree_children__(
                    model,
                    self._tree_[key]['children'][sub_key]['children'],
                    sub_item, sub_index,
                )

    def __load_tree_children__(self, model, section, parent, index):
        for key in section:
            sub_section = section[key]
            obj = sub_section['object']
            obj = self.__check_object_updates__(obj)
            item = TrTreeItem([obj.name, obj], parent)

            sub_row = sub_section['row']
            expanded = sub_section['expanded']
            sub_index = model.index(sub_row, 0, index)
            self.setExpanded(sub_index, expanded)

            self.__load_tree_children__(
                model,
                sub_section['children'],
                item, sub_index
            )

    def __check_object_updates__(self, obj):
        obj_schemas = [item['object'] for item in self._schema_ if isinstance(obj, item['object'])]
        obj_schema = obj_schemas[0] if obj_schemas else None
        if obj_schema is None:
            print('WARNING in {}: object type {} not in schema'.format(self.__class__.__name__, type(obj)))
            return obj
        else:
            new_obj = obj_schema.get_default()
            new_obj.update_object_from(obj)
            return new_obj

    def export_json(self):
        if not self._tree_:
            return
        tree_json = json.dumps(self._tree_, indent=4)
        print(tree_json)

        # json_file_path = self.config_file_path[:self.config_file_path.rfind('.')] + '.json'
        # with open(json_file_path, 'w') as f:
        #     json.dump(tree_json, f)

    def contextMenuEvent(self, pos):
        index = self.indexAt(pos)
        model = self.model()
        level = model.getLevel(index)
        items = self.get_schema_items_by_level(level)
        parent = model.itemFromIndex(index)
        menu = QMenu()
        for item in items:
            # Add new item
            add = QAction("Add {}".format(item['name']), menu)
            add.triggered.connect(lambda: self.add_child(index))
            add.setData(item['name'])
            menu.addAction(add)

        if parent is not None:
            menu.addSeparator()
            name = '{} "{}"'.format(parent.data[1].__class__.__name__,
                                    parent.data[1].name if parent.data[1] is not None else '')
            # remove current item
            rem = QAction()
            rem.setText("Remove {}".format(name))
            rem.triggered.connect(lambda: self.remove_item(index))
            menu.addAction(rem)
            # edit current item
            rename = QAction()
            rename.setText("Rename {}".format(name))
            rename.triggered.connect(lambda: self.edit_item(index))
            menu.addAction(rename)
        # show context menu
        menu.exec(self.mapToGlobal(pos))

    def model(self):
        return super().model()

    def setModel(self, model):
        super().setModel(model)

    # Editing
    def get_schema_items_by_level(self, level: int) -> list:
        return [s for s in self._schema_ if s['level'] == level]

    def get_schema_item_by_level_and_name(self, level: int, name: str) -> dict:
        items = self.get_schema_items_by_level(level)
        selection = [item for item in items if item['name'] == name]
        item = selection[0] if selection else {}
        return item

    def get_structure_item(self, level) -> dict:
        return self._schema_[level] if 0 <= level < len(self._schema_) else {}

    @staticmethod
    def get_new_object_instance(obj, level):
        # get a new default object
        if obj is None:
            return None
        new_obj = obj.get_default()
        new_obj.level = level
        return new_obj

    def add_child(self, index):

        model = self.model()
        level = model.getLevel(index)
        name = self.sender().data()
        new_item = self.get_schema_item_by_level_and_name(level, name)
        # new_item = self.get_structure_item(level)

        if 'object' in new_item:
            new_obj = self.get_new_object_instance(new_item['object'], level)
            new_item = TrTreeItem([new_obj.name, new_obj], model.itemFromIndex(index))
        else:
            new_item = TrTreeItem(['New Item', None], model.itemFromIndex(index))

        if self.header().count() == 0:
            # re-initialize model
            model = TrTreeModel()
            model.appendRow(new_item)
            self.setModel(model)
            self.hideColumn(1)
        else:
            # add node to existing model
            node = model.itemFromIndex(index)
            node.append_child(new_item)
        self.expandRecursively(index)
        # self.expandAll()

    def remove_item(self, index):
        model = self.model()
        model.removeRow(index.row(), index.parent())

    def edit_item(self, index):
        self.edit(index)

    def update_item(self, obj):

        model = self.model()
        index = self.currentIndex()
        item = model.itemFromIndex(index)
        item.data[1] = obj
        item.data[0] = obj.name
        model.dataChanged.emit(index, index)

    # Structure
    def get_tree_and_flat_structure(self) -> (dict, list):
        tree = dict()
        flat = list()
        id_ = 0

        root_item = self.model().root
        name = root_item.data[0]
        pobj = root_item.data[1]

        flat.append({'name': name, 'object': pobj})
        tree.update({
            name: {
                'row': root_item.row(),
                'expanded': True,
                'name': name,
                'object': pobj,
            }})
        flat, children_tree, _ = \
            self.__get_tree_and_flat_structure_get_children__(root_item, QModelIndex(), pobj, flat, {}, id_)
        tree[name].update({'children': children_tree})
        return tree, flat

    def __get_tree_and_flat_structure_get_children__(self, parent, index_, pobj, flat, tree, id_):
        for item in parent.children:
            name = item.data[0]
            obj = item.data[1]
            sub_index = self.model().index(item.row(), 0, index_)

            if obj is not None:
                obj.id = id_
                obj.name = name
                obj.parent = pobj.id if pobj is not None else None
                id_ += 1
            item.data[1] = obj
            flat.append({'name': name, 'object': obj})
            identity = '{}{}'.format(name, item.row())
            tree.update({
                identity: {
                    'row': item.row(),
                    'expanded': self.isExpanded(sub_index),
                    'name': name,
                    'object': obj,
                }})
            flat, children_tree, id_ = \
                self.__get_tree_and_flat_structure_get_children__(item, sub_index, obj, flat, {}, id_)
            tree[identity].update({'children': children_tree})

        return flat, tree, id_

    def show_flat_structure(self):
        self.update_all()
        print('-' * 100)
        print('FLAT Structure:')
        for row in self._flat_:
            print('  {}'.format(row))
        print('-' * 100)

    def show_tree_structure(self):
        self.update_all()
        print('-' * 100)
        print('TREE Structure:')
        for key in self._tree_:
            item = deepcopy(self._tree_[key])
            del item['children']
            print('{}'.format(item))
            indent = 0
            self.__show_tree_structure_children__(self._tree_[key]['children'], indent)
        print('-' * 100)

    def __show_tree_structure_children__(self, section: dict, indent: int):
        indent += 2
        for key in section:
            item = deepcopy(section[key])
            del item['children']
            print('{}{}'.format(' ' * indent, item))
            self.__show_tree_structure_children__(section[key]['children'], indent)

