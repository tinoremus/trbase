__version__ = '0.01'
import os
import sys
import datetime
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from trbase.pyqtwidgets.configwidget.templates import Templates
from trbase.pyqtwidgets.dataclasseditwidget.dataclasseditwidget import DataclassEditable, DataclassEditWidget
from trbase.pyqtwidgets.trqwidget import TrQWidget
from trbase.pyqtwidgets.tree.itemtree.itemtree import TrItemTreeWidget, TrItemTreeObject, PickableQPixmap
from trbase.pyqtwidgets.tree.itemtree.itemtree import TrItemTreeItem
from dataclasses import dataclass
from typing import List

try:
    from ui_templateapp import *
except ModuleNotFoundError:
    from .ui_templateapp import *
DEFAULT_DATE = datetime.date(2022, 1, 1)


@dataclass()
class TemplateEditableItem(TrItemTreeObject):
    integer_value_01: int = 0
    integer_value_02: int = 0

    def get_editable_buy_scenario(self) -> DataclassEditable:
        edit_widget = DataclassEditable(self)
        edit_widget.add_editable_value(
            name='integer_value_01',
            value=self.integer_value_01,
            template=Templates.CurrencySpinBox,
            options={'min_max': [0, 100000000], 'currency': '$', 'separate': True, 'decimals': 2},
        )
        return edit_widget


class TemplateTreeWidget(TrItemTreeWidget):
    def __init__(self, parent=None, sqlite_file_name: str = 'template'):
        super().__init__(parent=parent, sqlite_file_name=sqlite_file_name)

    @staticmethod
    def get_item_objects() -> List[TrItemTreeObject]:
        red_icon = QPixmap(50, 50)
        red_icon.fill(QColor("red"))

        blue_icon = QPixmap(50, 50)
        blue_icon.fill(QColor("blue"))

        green_icon = QPixmap(50, 50)
        green_icon.fill(QColor("green"))

        objects = [
            TemplateEditableItem(name='Editable Item', icon=PickableQPixmap(red_icon)),
        ]
        return objects


class TemplateApp(TrQWidget, Ui_Form):

    def __init__(self, **kwargs):
        """ initialize class """

        try:
            super().__init__()
            self.setupUi(self)

            if getattr(sys, 'frozen', False):
                self.home_path = os.path.dirname(sys.executable)
            elif __file__:
                self.home_path = os.path.dirname(__file__)

            self.tw_template = TemplateTreeWidget(self)
            # noinspection PyUnresolvedReferences
            self.tw_template.clicked.connect(self.show_item)
            self.vl_template_tree.addWidget(self.tw_template)

            self.config_widget: DataclassEditWidget or None = None
            self.config_object: any = None
            self.config_item: TrItemTreeItem or None = None
            self.config_node: QTreeWidgetItem or None = None
            self.connect()
            self.update_log('Starting GUI')

        except Exception as e:
            # noinspection PyProtectedMember,PyUnresolvedReferences
            self.__error_entry__(sys._getframe().f_code.co_name, e)

    def connect(self):
        try:
            pass
        except Exception as e:
            # noinspection PyProtectedMember,PyUnresolvedReferences
            self.__error_entry__(sys._getframe().f_code.co_name, e)

    def show_item(self):
        if self.config_widget is not None:
            self.config_widget.setParent(None)
        self.config_widget = None
        self.config_item = None
        self.config_object = None
        self.config_node = None

        self.repaint()

        self.config_item, self.config_node = self.tw_template.get_current_item()
        self.config_object = self.tw_template.get_current_object()

        self.__show_config_page__()

    def __show_config_page__(self):
        if isinstance(self.config_object, TemplateEditableItem):
            edit_obj = self.config_object.get_editable_buy_scenario()
            self.config_widget = DataclassEditWidget(edit_obj)
            self.hl_config.addWidget(self.config_widget)
            self.config_widget.config_update_signal.connect(self.update_item)

    def update_item(self):
        if self.config_widget is None:
            return
        self.tw_template.update_item(self.config_item, self.config_object)


# start GUI ===========================================================================================================
if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = TemplateApp()

    app.setOrganizationName("Remus Engineering")
    app.setOrganizationDomain("remus-engineering.tech")
    app.setApplicationName("Template App v{}".format(__version__))
    app.setWindowIcon(QIcon(os.path.join(gui.home_path, 'appicon.ico')))
    gui.setWindowTitle('{}'.format(app.applicationName()))
    gui.show()
    sys.exit(app.exec())
