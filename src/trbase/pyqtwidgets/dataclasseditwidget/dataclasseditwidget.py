from typing import List
from dataclasses import dataclass, field
from trbase.pyqtwidgets.configwidget.templates import Templates
from trbase.pyqtwidgets.checkboxgroup.checkboxgroup import QCheckBoxGroup
from trbase.pyqtwidgets.editlistwidget.editlistwidget import QEditListWidget
from trbase.std.trtable import TrTable
from trbase.pyqtwidgets.helper import trtable_to_qttablewidget
from trbase.pyqtwidgets.edittablewidget.edittablewidget import QEditTableWidget
import os
import datetime
from PyQt6.QtCore import QCoreApplication, pyqtSignal, Qt
from PyQt6.QtWidgets import *
from icecream import ic


@dataclass()
class DataclassEditableItem:
    template: Templates
    name: str
    value: any or List[any] or TrTable = None
    handle: QWidget or None = None
    position: int = -1
    editable: bool = True
    render: bool = True
    options: dict or None = None


@dataclass()
class DataclassEditable:
    obj: dataclass
    editable_items: List[DataclassEditableItem] = field(default_factory=list)

    def add_editable_value(
            self, name: str, value: any, template: Templates, position: int = -1,
            editable: bool = True, render: bool = True, options: dict or None = None):
        item = DataclassEditableItem(
            name=name, value=value, template=template, position=position, editable=editable, render=render,
            options=options
        )
        self.editable_items.append(item)

    def add_vertical_spacer(self):
        item = DataclassEditableItem(Templates.VerticalSpacer, name='Spacer')
        self.editable_items.append(item)


class DataclassEditWidget(QWidget):
    config_update_signal = pyqtSignal()

    def __init__(self, editable_dataclass_object: DataclassEditable):
        super().__init__()
        self.last_selection_path = ''
        self.dce = editable_dataclass_object
        self.save_button = self.__setup_save_button__()
        self.__setup_widget__()

    def __setup_save_button__(self):
        save_button = QPushButton()
        save_button.setText('Save')
        # noinspection PyUnresolvedReferences
        save_button.clicked.connect(self.__save__)
        _translate = QCoreApplication.translate
        save_button.setShortcut(_translate("Form", "Ctrl+S"))

        return save_button

    def __save__(self):
        for item in self.dce.editable_items:
            if item.handle is None:
                print('Can\'t save. No handle available to get value from. - {}'.format(item.name))
                continue
            if item.template in [Templates.LineEdit, Templates.LineEditSelectPath, Templates.LineEditSelectFile]:
                item.value = item.handle.text()
            elif item.template == Templates.TextEdit:
                item.value = item.handle.toPlainText()
            elif item.template == Templates.ComboBox:
                item.value = item.handle.currentData(Qt.ItemDataRole.UserRole)
            elif item.template in [Templates.DateEdit, Templates.DateEditTodayButton]:
                item.value = datetime.datetime.fromordinal(item.handle.date().toPyDate().toordinal()).timestamp()
            elif item.template in [Templates.DateTimeEdit, Templates.DateTimeEditNowButton]:
                item.value = item.handle.dateTime().toPyDateTime().timestamp()
            elif item.template == Templates.SpinBox:
                item.value = int(item.handle.value())
            elif item.template == Templates.DoubleSpinBox:
                item.value = float(item.handle.value())
            elif item.template == Templates.CurrencySpinBox:
                item.value = int(item.handle.value() * 100)
            elif item.template == Templates.CheckBox:
                item.value = True if item.handle.checkState().value else False
            elif item.template == Templates.CheckBoxGroup:
                item.value = item.handle.config
            elif item.template == Templates.ListEdit:
                item.value = list()
                for i in range(item.handle.list_widget.count()):
                    list_widget_item = item.handle.list_widget.item(i)
                    item.value.append(list_widget_item.text())
            elif item.template == Templates.TableEdit:
                item.value = item.handle.table
            elif item.template in [Templates.PushButton, Templates.ListStatic, Templates.VerticalSpacer]:
                continue  # ignore
            else:
                print('ConfigWidget: widget type "{}" not implemented yet'.format(item.template))
                continue
            self.dce.obj.__setattr__(item.name, item.value)
        # noinspection PyUnresolvedReferences
        self.config_update_signal.emit()

    def __get_handle_by_pb_name__(self, pb_name):
        handles = [item.handle for item in self.dce.editable_items if item.name == pb_name]
        handle = handles[0] if handles else None
        return handle

    def __select_path__(self):
        handle = self.__get_handle_by_pb_name__(self.sender().objectName())
        if handle is None:
            return
        # options = QFileDialog.Option.Options()
        # options |= QFileDialog.DontUseNativeDialog
        path = QFileDialog.getExistingDirectory(self, "Select Folder", self.last_selection_path)  # options=options
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

    @staticmethod
    def __get_title__(name):
        return name.title().replace('_', ' ')

    def __get_sorted_item_info_list__(self) -> List[DataclassEditableItem]:
        item_info_list = self.dce.editable_items
        return item_info_list

    def __setup_widget__(self):
        # initialize Group Box
        group_box = QGroupBox()
        group_box.setTitle("Configure {}".format(self.dce.__class__.__name__))

        # add items to grid
        grid = QGridLayout(group_box)
        grid.setSpacing(0)
        grid.setHorizontalSpacing(6)

        row = 0
        for item_info in self.__get_sorted_item_info_list__():
            if item_info.template == Templates.LineEdit:
                label = self.__setup_line_edit__(item_info)
                row = self.__add_widget_to_grid__(grid, label, item_info.handle, row)
            elif item_info.template == Templates.LineEditSelectPath:
                label = self.__setup_line_edit__(item_info)
                hl = self.__add_select_path_push_button__(item_info)
                row = self.__add_widget_to_grid__(grid, label, hl, row)
            elif item_info.template == Templates.LineEditSelectFile:
                label = self.__setup_line_edit__(item_info)
                hl = self.__add_select_file_push_button__(item_info)
                row = self.__add_widget_to_grid__(grid, label, hl, row)
            elif item_info.template == Templates.TextEdit:
                label = self.__setup_text_edit__(item_info)
                row = self.__add_widget_to_grid__(grid, label, item_info.handle, row)
            elif item_info.template == Templates.ComboBox:
                label = self.__setup_combo_box__(item_info)
                row = self.__add_widget_to_grid__(grid, label, item_info.handle, row)
            elif item_info.template == Templates.DateEdit:
                label, _ = self.__setup_date_edit__(item_info)
                row = self.__add_widget_to_grid__(grid, label, item_info.handle, row)
            elif item_info.template == Templates.DateEditTodayButton:
                label, hl = self.__setup_date_edit__(item_info)
                row = self.__add_widget_to_grid__(grid, label, hl, row)
            elif item_info.template == Templates.DateTimeEdit:
                label, _ = self.__setup_date_time_edit__(item_info)
                row = self.__add_widget_to_grid__(grid, label, item_info.handle, row)
            elif item_info.template == Templates.DateTimeEditNowButton:
                label, hl = self.__setup_date_time_edit__(item_info)
                row = self.__add_widget_to_grid__(grid, label, hl, row)
            elif item_info.template == Templates.SpinBox:
                label = self.__setup_spin_box__(item_info)
                row = self.__add_widget_to_grid__(grid, label, item_info.handle, row)
            elif item_info.template == Templates.DoubleSpinBox:
                label, _ = self.__setup_double_spin_box__(item_info)
                row = self.__add_widget_to_grid__(grid, label, item_info.handle, row)
            elif item_info.template == Templates.CurrencySpinBox:
                label, _ = self.__setup_currency_spin_box__(item_info)
                row = self.__add_widget_to_grid__(grid, label, item_info.handle, row)
            elif item_info.template == Templates.CheckBox:
                label = self.__setup_check_box__(item_info)
                row = self.__add_widget_to_grid__(grid, label, item_info.handle, row)
            elif item_info.template == Templates.CheckBoxGroup:
                label = self.__setup_check_box_group__(item_info)
                row = self.__add_widget_to_grid__(grid, label, item_info.handle, row)
            elif item_info.template == Templates.PushButton:
                label = self.__setup_push_button__(item_info)
                row = self.__add_widget_to_grid__(grid, label, item_info.handle, row)
            elif item_info.template == Templates.ListStatic:
                label = self.__setup_list_static__(item_info)
                row = self.__add_widget_to_grid__(grid, label, item_info.handle, row)
            elif item_info.template == Templates.ListEdit:
                label = self.__setup_list_edit__(item_info)
                row = self.__add_widget_to_grid__(grid, label, item_info.handle, row)
            elif item_info.template == Templates.TableStatic:
                label = self.__setup_table_static__(item_info)
                row = self.__add_widget_to_grid__(grid, label, item_info.handle, row)
            elif item_info.template == Templates.TableEdit:
                label = self.__setup_table_edit__(item_info)
                row = self.__add_widget_to_grid__(grid, label, item_info.handle, row)
            elif item_info.template == Templates.VerticalSpacer:
                label, handle = self.__setup_vertical_spacer__()
                row = self.__add_widget_to_grid__(grid, label, handle, row)
            else:
                print(f'not implemented yet: {item_info.template}')

        # add save button
        row += 1
        grid.addWidget(self.save_button, row, 1, 1, 1)

        # finalize setup
        page_layout = QVBoxLayout()
        page_layout.addWidget(group_box)
        self.setLayout(page_layout)

    @staticmethod
    def __add_widget_to_grid__(grid: QGridLayout, label, handle, row: int) -> int:
        if isinstance(label, QWidget):
            grid.addWidget(label, row, 0, 1, 1)
        elif isinstance(label, QLayout):
            grid.addLayout(label, row, 0, 1, 1)
        if isinstance(handle, QWidget):
            grid.addWidget(handle, row, 1, 1, 1)
        elif isinstance(handle, QLayout):
            grid.addLayout(handle, row, 1, 1, 1)
        row += 1
        return row

    def __setup_line_edit__(self, item: DataclassEditableItem):
        label = QLabel(self.__get_title__(item.name))
        handle = QLineEdit()
        handle.setPlaceholderText(item.name.title())
        handle.setText(str(item.value))
        handle.setEnabled(item.editable)
        item.handle = handle
        return label

    def __add_select_path_push_button__(self, item: DataclassEditableItem):
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(item.handle)
        if isinstance(item.handle, QLineEdit):
            item.handle.setPlaceholderText('Select folder ...')
        pb = QPushButton()
        pb.setObjectName(item.name)
        pb.setText('...')
        pb.setFixedWidth(20)
        # noinspection PyUnresolvedReferences
        pb.clicked.connect(self.__select_path__)
        horizontal_layout.addWidget(pb)

        return horizontal_layout

    def __add_select_file_push_button__(self, item: DataclassEditableItem):
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(item.handle)
        if isinstance(item.handle, QLineEdit):
            item.handle.setPlaceholderText('Select file ...')
        pb = QPushButton()
        pb.setObjectName(item.name)
        pb.setText('...')
        pb.setFixedWidth(20)
        # noinspection PyUnresolvedReferences
        pb.clicked.connect(self.__select_file__)
        horizontal_layout.addWidget(pb)

        return horizontal_layout

    def __setup_text_edit__(self, item: DataclassEditableItem):
        vertical_layout = QVBoxLayout()
        label = QLabel(self.__get_title__(item.name))
        vertical_layout.addWidget(label)
        label_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        vertical_layout.addItem(label_spacer)
        handle = QTextEdit()
        handle.setPlaceholderText(item.name.title())
        handle.setText(str(item.value))
        handle.setEnabled(item.editable)
        item.handle = handle
        return vertical_layout

    def __setup_combo_box__(self, item: DataclassEditableItem):
        label = QLabel(self.__get_title__(item.name))
        handle = QComboBox()
        options = item.options
        index = [o.name for o in options].index(item.value.name) if item.value in options else 0
        for option in options:
            handle.addItem(option.name, option)
            # item.setData(Qt.UserRole, option)
        handle.setCurrentIndex(index)
        handle.setEnabled(item.editable)
        item.handle = handle
        return label

    def __setup_date_edit__(self, item: DataclassEditableItem):
        label = QLabel(self.__get_title__(item.name))

        handle = QDateEdit()
        handle.setDisplayFormat('MM/dd/yyyy')
        handle.setCalendarPopup(True)
        handle.setDate(datetime.datetime.fromtimestamp(item.value))
        handle.setEnabled(item.editable)
        item.handle = handle

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(handle)
        pb = QPushButton()
        pb.setObjectName(item.name)
        pb.setText('today')
        pb.setFixedWidth(50)
        # noinspection PyUnresolvedReferences
        pb.clicked.connect(self.__set_date_edit_to_today__)
        horizontal_layout.addWidget(pb)

        return label, horizontal_layout

    def __setup_date_time_edit__(self, item: DataclassEditableItem):
        label = QLabel(self.__get_title__(item.name))
        handle = QDateTimeEdit()
        handle.setDisplayFormat('MM/dd/yyyy HH:mm:ss')
        handle.setCalendarPopup(True)
        handle.setDateTime(datetime.datetime.fromtimestamp(item.value))
        handle.setEnabled(item.editable)
        item.handle = handle
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(handle)
        pb = QPushButton()
        pb.setObjectName(item.name)
        pb.setText('now')
        pb.setFixedWidth(50)
        # noinspection PyUnresolvedReferences
        pb.clicked.connect(self.__set_date_time_edit_to_today__)
        horizontal_layout.addWidget(pb)
        return label, horizontal_layout

    def __setup_spin_box__(self, item: DataclassEditableItem):
        label = QLabel(self.__get_title__(item.name))
        handle = QSpinBox()
        handle.setEnabled(item.editable)
        if isinstance(item.options, dict):
            min_max = item.options['min_max'] if 'min_max' in item.options else [0, 10]
            handle.setRange(min_max[0], min_max[1])
            prefix = item.options['prefix'] if 'prefix' in item.options else ''
            handle.setPrefix(prefix)
            separate = item.options['separate'] if 'separate' in item.options else False
            handle.setGroupSeparatorShown(separate)
        handle.setValue(int(item.value))
        item.handle = handle
        return label

    def __setup_double_spin_box__(self, item: DataclassEditableItem):
        label = QLabel(self.__get_title__(item.name))

        handle = QDoubleSpinBox()
        if isinstance(item.options, dict):
            min_max = item.options['min_max'] if 'min_max' in item.options else [0, 10]
            handle.setRange(min_max[0], min_max[1])
            decimals = item.options['decimals'] if 'decimals' in item.options else 0
            handle.setDecimals(decimals)
            prefix = item.options['prefix'] if 'prefix' in item.options else ''
            handle.setPrefix(prefix)
            separate = item.options['separate'] if 'separate' in item.options else False
            handle.setGroupSeparatorShown(separate)
        handle.setValue(float(item.value))
        handle.setEnabled(item.editable)
        item.handle = handle

        return label, handle

    def __setup_currency_spin_box__(self, item: DataclassEditableItem):
        label = QLabel(self.__get_title__(item.name))

        handle = QDoubleSpinBox()
        if isinstance(item.options, dict):
            min_max = item.options['min_max'] if 'min_max' in item.options else [0, 10]
            handle.setRange(min_max[0], min_max[1])
            decimals = item.options['decimals'] if 'decimals' in item.options else 2
            handle.setDecimals(decimals)
            currency = item.options['currency'] if 'currency' in item.options else ''
            handle.setPrefix(currency)
            separate = item.options['separate'] if 'separate' in item.options else False
            handle.setGroupSeparatorShown(separate)
        handle.setValue(item.value / 100)
        handle.setEnabled(item.editable)
        item.handle = handle

        return label, handle

    def __setup_check_box__(self, item: DataclassEditableItem):
        label = QLabel(self.__get_title__(item.name))
        handle = QCheckBox()
        handle.setChecked(item.value)
        handle.setEnabled(item.editable)
        item.handle = handle
        return label

    def __setup_check_box_group__(self, item: DataclassEditableItem):
        label = QLabel(self.__get_title__(item.name))

        rows = item.options['rows'] if 'rows' in item.options else 1
        columns = item.options['columns'] if 'columns' in item.options else 1
        handle = QCheckBoxGroup(None, item.value, rows, columns)

        # handle.setText(str(value))
        handle.setEnabled(item.editable)
        item.handle = handle
        return label

    @staticmethod
    def __setup_push_button__(item: DataclassEditableItem):
        handle = QPushButton()
        handle.setText(str(item.value))
        handle.setEnabled(item.editable)
        item.handle = handle

        return handle

    def __setup_list_static__(self, item: DataclassEditableItem):
        vertical_layout = QVBoxLayout()
        label = QLabel(self.__get_title__(item.name))
        vertical_layout.addWidget(label)
        label_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        vertical_layout.addItem(label_spacer)

        handle = QListWidget()
        if isinstance(item.value, list):
            for value in item.value:
                widget_item = QListWidgetItem()
                widget_item.setText(value)
                handle.addItem(widget_item)
        handle.setEnabled(item.editable)
        item.handle = handle

        return vertical_layout, handle

    def __setup_list_edit__(self, item: DataclassEditableItem):
        vertical_layout = QVBoxLayout()
        label = QLabel(self.__get_title__(item.name))
        vertical_layout.addWidget(label)
        label_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        vertical_layout.addItem(label_spacer)

        handle = QEditListWidget()
        if isinstance(item.value, list):
            for value in item.value:
                widget_item = QListWidgetItem()
                widget_item.setText(value)
                handle.list_widget.addItem(widget_item)
        handle.setEnabled(item.editable)
        item.handle = handle

        return vertical_layout

    def __setup_table_static__(self, item: DataclassEditableItem):
        vertical_layout = QVBoxLayout()
        label = QLabel(self.__get_title__(item.name))
        vertical_layout.addWidget(label)
        label_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        vertical_layout.addItem(label_spacer)

        handle = QTableWidget()
        if item.value is not None:
            trtable_to_qttablewidget(item.value, handle)
        handle.setEnabled(item.editable)
        item.handle = handle

        return vertical_layout

    def __setup_table_edit__(self, item: DataclassEditableItem):
        vertical_layout = QVBoxLayout()
        label = QLabel(self.__get_title__(item.name))
        vertical_layout.addWidget(label)
        label_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        vertical_layout.addItem(label_spacer)

        handle = QEditTableWidget()
        if item.value is not None:
            handle.set_table(item.value)
        handle.setEnabled(item.editable)
        item.handle = handle

        return vertical_layout, handle

    @staticmethod
    def __setup_vertical_spacer__():
        label = QLabel('')
        handle = QSpacerItem(20, 445, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # handle.setAlignment( Qt.AlignmentFlag.AlignTop)
        return label, handle
