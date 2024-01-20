import datetime
import os

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from trbase.pyqtwidgets.checkboxgroup.checkboxgroup import QCheckBoxGroup
from trbase.pyqtwidgets.configwidget.configwidgetitem import ConfigWidgetItem
from trbase.pyqtwidgets.configwidget.templates import Templates
from trbase.pyqtwidgets.editlistwidget.editlistwidget import QEditListWidget
from trbase.std.trtable import TrTable
from trbase.pyqtwidgets.helper import trtable_to_qttablewidget
from trbase.pyqtwidgets.edittablewidget.edittablewidget import QEditTableWidget

from src.trbase.pyqtwidgets.helper import trtable_to_qttablewidget


class ConfigWidget(QWidget):
    config_update_signal = pyqtSignal()

    def __init__(self, index: QModelIndex or None, obj: ConfigWidgetItem or None):
        super().__init__()
        self.index = index
        self.obj = obj
        self.info = self.obj.get_edit_items() if self.obj is not None else {}
        self.handles = dict()

        self.save_button = self.__setup_save_button__()
        self.last_selection_path = str()
        self.setup_widget()

    def setup_widget(self):
        if self.obj is None:
            return
        # initialize Group Box
        group_box = QGroupBox()
        group_box.setTitle("Configure {}".format(self.obj.__class__.__name__))

        # add items to grid
        grid = QGridLayout(group_box)
        grid.setSpacing(0)
        grid.setHorizontalSpacing(6)

        row = 0
        sorted_info = dict(sorted(self.info.items(), key=lambda item: item[1]['position']))
        for name in sorted_info:
            # print(name, self.info[name])
            if self.info[name]['template'] == Templates.LineEdit:
                label, handle = self.__setup_line_edit__(name)
                grid.addWidget(label, row, 0, 1, 1)
                grid.addWidget(handle, row, 1, 1, 1)

                if self.info[name]['editable']:
                    self.handles.update({name: handle})
                row += 1

            elif self.info[name]['template'] == Templates.LineEditSelectPath:
                label, handle = self.__setup_line_edit__(name)
                hl = self.__add_select_path_push_button__(name, handle)
                grid.addWidget(label, row, 0, 1, 1)
                grid.addLayout(hl, row, 1, 1, 1)

                if self.info[name]['editable']:
                    self.handles.update({name: handle})
                row += 1

            elif self.info[name]['template'] == Templates.LineEditSelectFile:
                label, handle = self.__setup_line_edit__(name)
                hl = self.__add_select_file_push_button__(name, handle)
                grid.addWidget(label, row, 0, 1, 1)
                grid.addLayout(hl, row, 1, 1, 1)

                if self.info[name]['editable']:
                    self.handles.update({name: handle})
                row += 1

            elif self.info[name]['template'] == Templates.TextEdit:
                vertical_layout, handle = self.__setup_text_edit__(name)
                grid.addLayout(vertical_layout, row, 0, 1, 1)
                grid.addWidget(handle, row, 1, 1, 1)

                if self.info[name]['editable']:
                    self.handles.update({name: handle})
                row += 1

            elif self.info[name]['template'] == Templates.ComboBox:
                label, handle = self.__setup_combo_box__(name)
                grid.addWidget(label, row, 0, 1, 1)
                grid.addWidget(handle, row, 1, 1, 1)

                if self.info[name]['editable']:
                    self.handles.update({name: handle})
                row += 1

            elif self.info[name]['template'] == Templates.DateEdit:
                label, handle, hl = self.__setup_date_edit__(name)
                grid.addWidget(label, row, 0, 1, 1)
                grid.addWidget(handle, row, 1, 1, 1)

                if self.info[name]['editable']:
                    self.handles.update({name: handle})
                row += 1

            elif self.info[name]['template'] == Templates.DateEditTodayButton:
                label, handle, hl = self.__setup_date_edit__(name)
                grid.addWidget(label, row, 0, 1, 1)
                grid.addLayout(hl, row, 1, 1, 1)

                if self.info[name]['editable']:
                    self.handles.update({name: handle})
                row += 1

            elif self.info[name]['template'] == Templates.DateTimeEdit:
                label, handle, hl = self.__setup_date_time_edit__(name)
                grid.addWidget(label, row, 0, 1, 1)
                grid.addWidget(handle, row, 1, 1, 1)

                if self.info[name]['editable']:
                    self.handles.update({name: handle})
                row += 1

            elif self.info[name]['template'] == Templates.DateTimeEditNowButton:
                label, handle, hl = self.__setup_date_time_edit__(name)
                grid.addWidget(label, row, 0, 1, 1)
                grid.addLayout(hl, row, 1, 1, 1)

                if self.info[name]['editable']:
                    self.handles.update({name: handle})
                row += 1

            elif self.info[name]['template'] == Templates.SpinBox:
                label, handle = self.__setup_spin_box__(name)
                grid.addWidget(label, row, 0, 1, 1)
                grid.addWidget(handle, row, 1, 1, 1)

                if self.info[name]['editable']:
                    self.handles.update({name: handle})
                row += 1

            elif self.info[name]['template'] == Templates.DoubleSpinBox:
                label, handle = self.__setup_double_spin_box__(name)
                grid.addWidget(label, row, 0, 1, 1)
                grid.addWidget(handle, row, 1, 1, 1)

                if self.info[name]['editable']:
                    self.handles.update({name: handle})
                row += 1

            elif self.info[name]['template'] == Templates.CheckBox:
                label, handle = self.__setup_check_box__(name)
                grid.addWidget(label, row, 0, 1, 1)
                grid.addWidget(handle, row, 1, 1, 1)

                if self.info[name]['editable']:
                    self.handles.update({name: handle})
                row += 1

            elif self.info[name]['template'] == Templates.CheckBoxGroup:
                label, handle = self.__setup_check_box_group__(name)
                grid.addWidget(label, row, 0, 1, 1)
                grid.addWidget(handle, row, 1, 1, 1)

                if self.info[name]['editable']:
                    self.handles.update({name: handle})
                row += 1

            elif self.info[name]['template'] == Templates.PushButton:
                handle = self.__setup_push_button__(name)
                grid.addWidget(handle, row, 1, 1, 1)

                if self.info[name]['editable']:
                    self.handles.update({name: handle})
                row += 1

            elif self.info[name]['template'] == Templates.ListStatic:
                vertical_layout, handle = self.__setup_list_static__(name)
                grid.addLayout(vertical_layout, row, 0, 1, 1)
                grid.addWidget(handle, row, 1, 1, 1)

                if self.info[name]['editable']:
                    self.handles.update({name: handle})
                row += 1

            elif self.info[name]['template'] == Templates.ListEdit:
                vertical_layout, handle = self.__setup_list_edit__(name)
                grid.addLayout(vertical_layout, row, 0, 1, 1)
                grid.addWidget(handle, row, 1, 1, 1)

                if self.info[name]['editable']:
                    self.handles.update({name: handle})
                row += 1

            elif self.info[name]['template'] == Templates.TableStatic:
                vertical_layout, handle = self.__setup_table_static__(name)
                grid.addLayout(vertical_layout, row, 0, 1, 1)
                grid.addWidget(handle, row, 1, 1, 1)

                if self.info[name]['editable']:
                    self.handles.update({name: handle})
                row += 1

            elif self.info[name]['template'] == Templates.TableEdit:
                vertical_layout, handle = self.__setup_table_edit__(name)
                grid.addLayout(vertical_layout, row, 0, 1, 1)
                grid.addWidget(handle, row, 1, 1, 1)

                if self.info[name]['editable']:
                    self.handles.update({name: handle})
                row += 1

            elif self.info[name]['template'] == Templates.VerticalSpacer:
                vertical_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
                grid.addItem(vertical_spacer, row, 1, 1, 1)
                row += 1

            else:
                print('ConfigWidget: widget type "{}" not implemented yet'.format(
                    self.info[name]['template']))

        # add save button
        row += 1
        grid.addWidget(self.save_button, row, 1, 1, 1)

        # finalize setup
        page_layout = QVBoxLayout()
        page_layout.addWidget(group_box)
        self.setLayout(page_layout)

    def set_last_selection_path(self, value: str) -> bool:
        if not isinstance(value, str):
            return False
        self.last_selection_path = value
        return True

    @staticmethod
    def __get_title__(name):
        return name.title().replace('_', ' ')

    def __setup_line_edit__(self, name):
        label = QLabel(self.__get_title__(name))

        handle = QLineEdit()
        handle.setPlaceholderText(name.title())
        value = self.obj.__getattribute__(name)
        handle.setText(str(value))
        handle.setEnabled(self.info[name]['editable'])

        return label, handle

    def __add_select_path_push_button__(self, name, handle):
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(handle)
        if isinstance(handle, QLineEdit):
            handle.setPlaceholderText('Select folder ...')
        pb = QPushButton()
        pb.setObjectName(name)
        pb.setText('...')
        pb.setFixedWidth(20)
        pb.clicked.connect(self.__select_path__)
        horizontal_layout.addWidget(pb)

        return horizontal_layout

    def __add_select_file_push_button__(self, name, handle):
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(handle)
        if isinstance(handle, QLineEdit):
            handle.setPlaceholderText('Select file ...')
        pb = QPushButton()
        pb.setObjectName(name)
        pb.setText('...')
        pb.setFixedWidth(20)
        pb.clicked.connect(self.__select_file__)
        horizontal_layout.addWidget(pb)

        return horizontal_layout

    def __setup_text_edit__(self, name):

        vertical_layout = QVBoxLayout()
        label = QLabel(self.__get_title__(name))
        vertical_layout.addWidget(label)
        label_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        vertical_layout.addItem(label_spacer)

        handle = QTextEdit()
        handle.setPlaceholderText(name.title())
        value = self.obj.__getattribute__(name)
        handle.setText(str(value))
        handle.setEnabled(self.info[name]['editable'])

        return vertical_layout, handle

    def __setup_combo_box__(self, name):
        label = QLabel(self.__get_title__(name))

        handle = QComboBox()
        value = self.obj.__getattribute__(name)
        options = self.info[name]['options']
        index = [o.name for o in options].index(value.name) if value in options else 0
        for option in options:
            handle.addItem(option.name, option)
            # item.setData(Qt.UserRole, option)

        handle.setCurrentIndex(index)
        handle.setEnabled(self.info[name]['editable'])

        return label, handle

    def __setup_date_edit__(self, name):
        label = QLabel(self.__get_title__(name))

        handle = QDateEdit()
        handle.setDisplayFormat('MM/dd/yyyy')
        handle.setCalendarPopup(True)
        value = self.obj.__getattribute__(name)
        handle.setDate(datetime.datetime.fromtimestamp(value))
        handle.setEnabled(self.info[name]['editable'])

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(handle)
        pb = QPushButton()
        pb.setObjectName(name)
        pb.setText('today')
        pb.setFixedWidth(50)
        pb.clicked.connect(self.__set_date_edit_to_today__)
        horizontal_layout.addWidget(pb)

        return label, handle, horizontal_layout

    def __setup_date_time_edit__(self, name):
        label = QLabel(self.__get_title__(name))

        handle = QDateTimeEdit()
        handle.setDisplayFormat('MM/dd/yyyy HH:mm:ss')
        handle.setCalendarPopup(True)
        value = self.obj.__getattribute__(name)
        handle.setDateTime(datetime.datetime.fromtimestamp(value))
        handle.setEnabled(self.info[name]['editable'])

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(handle)
        pb = QPushButton()
        pb.setObjectName(name)
        pb.setText('now')
        pb.setFixedWidth(50)
        pb.clicked.connect(self.__set_date_time_edit_to_today__)
        horizontal_layout.addWidget(pb)

        return label, handle, horizontal_layout

    def __setup_spin_box__(self, name):
        label = QLabel(self.__get_title__(name))

        handle = QSpinBox()
        value = self.obj.__getattribute__(name)
        options = self.info[name]['options'] if 'options' in self.info[name] else []
        if options:
            if len(options) >= 2:
                handle.setRange(options[0], options[1])
        handle.setValue(int(value))
        handle.setEnabled(self.info[name]['editable'])

        return label, handle

    def __setup_double_spin_box__(self, name):
        label = QLabel(self.__get_title__(name))

        handle = QDoubleSpinBox()
        value = self.obj.__getattribute__(name)
        options = self.info[name]['options'] if 'options' in self.info[name] else []
        if options:
            if len(options) >= 2:
                handle.setRange(options[0], options[1])
            if len(options) >= 3:
                handle.setDecimals(options[2])
        handle.setValue(float(value))
        handle.setEnabled(self.info[name]['editable'])

        return label, handle

    def __setup_check_box__(self, name):
        label = QLabel(self.__get_title__(name))

        handle = QCheckBox()
        value = self.obj.__getattribute__(name)
        handle.setChecked(value)
        handle.setEnabled(self.info[name]['editable'])

        return label, handle

    def __setup_check_box_group__(self, name):
        label = QLabel(self.__get_title__(name))

        options = self.info[name]['options']
        rows = options['rows'] if 'rows' in options else 1
        columns = options['columns'] if 'columns' in options else 1
        value = self.obj.__getattribute__(name)
        handle = QCheckBoxGroup(None, value, rows, columns)

        # handle.setText(str(value))
        handle.setEnabled(self.info[name]['editable'])

        return label, handle

    def __setup_push_button__(self, name):

        handle = QPushButton()
        value = self.obj.__getattribute__(name)
        handle.setText(str(value))
        handle.setEnabled(self.info[name]['editable'])

        return handle

    def __setup_save_button__(self):
        save_button = QPushButton()
        save_button.setText('Save')
        # noinspection PyUnresolvedReferences
        save_button.clicked.connect(self.save)
        _translate = QCoreApplication.translate
        save_button.setShortcut(_translate("Form", "Ctrl+S"))

        return save_button

    def __get_handle_by_pb_name__(self, pb_name):
        handles = [self.handles[name] for name in self.handles if name == pb_name]
        handle = handles[0] if handles else None
        return handle

    def __set_date_edit_to_today__(self):
        handle = self.__get_handle_by_pb_name__(self.sender().objectName())
        if handle is None:
            return
        handle.setDate(datetime.date.today())

    def __set_date_time_edit_to_today__(self):
        handle = self.__get_handle_by_pb_name__(self.sender().objectName())
        if handle is None:
            return
        handle.setDateTime(datetime.datetime.now())

    def __setup_list_static__(self, name):
        vertical_layout = QVBoxLayout()
        label = QLabel(self.__get_title__(name))
        vertical_layout.addWidget(label)
        label_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        vertical_layout.addItem(label_spacer)

        handle = QListWidget()
        values = self.obj.__getattribute__(name)
        if isinstance(values, list):
            for value in values:
                item = QListWidgetItem()
                item.setText(value)
                handle.addItem(item)
        handle.setEnabled(self.info[name]['editable'])

        return vertical_layout, handle

    def __setup_list_edit__(self, name):
        vertical_layout = QVBoxLayout()
        label = QLabel(self.__get_title__(name))
        vertical_layout.addWidget(label)
        label_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        vertical_layout.addItem(label_spacer)

        handle = QEditListWidget()
        values = self.obj.__getattribute__(name)
        if isinstance(values, list):
            for value in values:
                item = QListWidgetItem()
                item.setText(value)
                handle.list_widget.addItem(item)
        handle.setEnabled(self.info[name]['editable'])

        return vertical_layout, handle

    def __setup_table_static__(self, name):
        vertical_layout = QVBoxLayout()
        label = QLabel(self.__get_title__(name))
        vertical_layout.addWidget(label)
        label_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        vertical_layout.addItem(label_spacer)

        handle = QTableWidget()
        table = self.obj.__getattribute__(name)
        if isinstance(table, TrTable):
            trtable_to_qttablewidget(table, handle)
        handle.setEnabled(self.info[name]['editable'])

        return vertical_layout, handle

    def __setup_table_edit__(self, name):
        vertical_layout = QVBoxLayout()
        label = QLabel(self.__get_title__(name))
        vertical_layout.addWidget(label)
        label_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        vertical_layout.addItem(label_spacer)

        handle = QEditTableWidget()
        table = self.obj.__getattribute__(name)
        if isinstance(table, TrTable):
            handle.set_table(table)
        handle.setEnabled(self.info[name]['editable'])

        return vertical_layout, handle

    def __select_path__(self):
        handle = self.__get_handle_by_pb_name__(self.sender().objectName())
        if handle is None:
            return
        # options = QFileDialog.Option.Options()
        # options |= QFileDialog.DontUseNativeDialog
        path = QFileDialog.getExistingDirectory(
            self, "Select Folder", self.last_selection_path)  # options=options
        if not path:
            return
        self.last_selection_path = path
        handle.setText(path)

    def __select_file__(self):
        handle = self.__get_handle_by_pb_name__(self.sender().objectName())
        if handle is None:
            return
        # options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog

        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select File", self.last_selection_path,
            "All Files (*);;Python Files (*.py)")  # , options=options
        if not file_name:
            return
        self.last_selection_path = os.path.dirname(file_name)
        handle.setText(file_name)

    def save(self):
        for name in self.handles:
            handle = self.handles[name]
            if self.info[name]['template'] in [Templates.LineEdit,
                                               Templates.LineEditSelectPath,
                                               Templates.LineEditSelectFile]:
                value = handle.text()
            elif self.info[name]['template'] == Templates.TextEdit:
                value = handle.toPlainText()
            elif self.info[name]['template'] == Templates.ComboBox:
                value = handle.currentData(Qt.ItemDataRole.UserRole)
            elif self.info[name]['template'] in [Templates.DateEdit, Templates.DateEditTodayButton]:
                value = datetime.datetime.fromordinal(handle.date().toPyDate().toordinal()).timestamp()
            elif self.info[name]['template'] in [Templates.DateTimeEdit, Templates.DateTimeEditNowButton]:
                value = handle.dateTime().toPyDateTime().timestamp()
            elif self.info[name]['template'] == Templates.SpinBox:
                value = int(handle.value())
            elif self.info[name]['template'] == Templates.DoubleSpinBox:
                value = float(handle.value())
            elif self.info[name]['template'] == Templates.CheckBox:
                value = True if handle.checkState() else False
            elif self.info[name]['template'] == Templates.CheckBoxGroup:
                value = handle.config
            elif self.info[name]['template'] == Templates.ListEdit:
                value = list()
                for i in range(handle.list_widget.count()):
                    list_widget_item = handle.list_widget.item(i)
                    value.append(list_widget_item.text())
            elif self.info[name]['template'] == Templates.TableEdit:
                value = handle.table
            elif self.info[name]['template'] in [Templates.PushButton, Templates.ListStatic, Templates.VerticalSpacer]:
                # ignore
                continue
            else:
                print('ConfigWidget: widget type "{}" not implemented yet'.format(
                    self.info[name]['template']))
                continue
            self.obj.__setattr__(name, value)
        self.config_update_signal.emit()
