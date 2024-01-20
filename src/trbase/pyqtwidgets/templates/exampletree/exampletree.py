__version__ = '0.01'
import os
import sys
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from trbase.pyqtwidgets.trqwidget import TrQWidget
from trbase.pyqtwidgets.configwidget.configwidgetitem import ConfigWidgetItem
from trbase.pyqtwidgets.configwidget.configwidget import ConfigWidget
from trbase.pyqtwidgets.tree.trstructuretreeview import TrStructureTreeView
from trbase.std.trtable import TrTable
import inspect
from items.customer import Customer
from items.department import Department
from items.project import Project
from items.team import Team
from items.vehicle import Vehicle

try:
    from ui_exampletree import *
except ModuleNotFoundError:
    from .ui_exampletree import *


class ExampleTree(TrQWidget, Ui_Form):

    def __init__(self, **kwargs):
        """ initialize class """

        try:
            super().__init__()
            self.setupUi(self)

            if getattr(sys, 'frozen', False):
                self.home_path = os.path.dirname(sys.executable)
            elif __file__:
                self.home_path = os.path.dirname(__file__)

            self.splitter.setSizes([400, 500])

            # setup tree
            self.tree = TrStructureTreeView()
            self.tree.set_config_file_path(os.path.join(self.home_path, 'config.pkl'))
            self.tree.load_config()
            self.tree.set_schema(self.get_schema())
            self.vL_tree.addWidget(self.tree)

            self.config_widget = ConfigWidget(None, None)
            self.connect()

        except Exception as e:
            # noinspection PyProtectedMember,PyUnresolvedReferences
            self.__error_entry__(sys._getframe().f_code.co_name, e)

    @staticmethod
    def get_schema() -> list:
        # schema = [
        #     {'level': 0, 'name': 'Customer', 'object': Customer},
        #     {'level': 1, 'name': 'Department', 'object': Department},
        #     {'level': 2, 'name': 'Team', 'object': Team},
        #     {'level': 3, 'name': 'Project', 'object': Project},
        # ]
        schema = [
            {'level': 0, 'name': 'Customer', 'object': Customer},
            {'level': 1, 'name': 'Department', 'object': Department},
            {'level': 2, 'name': 'Team', 'object': Team},
            {'level': 3, 'name': 'Project', 'object': Project},
            {'level': 3, 'name': 'Vehicle', 'object': Vehicle},
        ]
        return schema

    # noinspection PyUnresolvedReferences
    def connect(self):
        try:
            self.tree.clicked.connect(self.show_node)
            self.pb_save_tree.clicked.connect(self.save_tree)
        except Exception as e:
            self.__error_entry__(inspect.currentframe().f_code.co_name, e)

    def save_tree(self):
        try:
            self.tree.save_config()
        except Exception as e:
            self.__error_entry__(inspect.currentframe().f_code.co_name, e)

    def show_node(self):
        if self.config_widget is not None:
            self.config_widget.setParent(None)
            self.config_widget = None
        self.repaint()
        try:
            index = self.tree.currentIndex()
            item = self.tree.model().itemFromIndex(index)
            obj = item.data[1]
            if not isinstance(obj, ConfigWidgetItem):
                return
            # self.tree.show_tree_structure()

            # if isinstance(obj, Project):
            #     obj.select_tflite_delegate = [
            #         {'name': 'CPU', 'state': True},
            #         {'name': 'GPU', 'state': True},
            #         {'name': 'NNAPI', 'state': True}
            #     ]W

            # if isinstance(obj, Team):
            #     table = Table()
            #     table.set_header(['ID', 'Name', 'Description'])
            #     table.set_table([
            #         [1, 'First Name', 'This is a first name item'],
            #         [1, 'Second Name', 'This is a second name item'],
            #     ])
            #     obj.my_table = table

            self.config_widget = ConfigWidget(index, obj)
            self.config_widget.config_update_signal.connect(self.update_node)
            print(self.config_widget.obj)

            if isinstance(self.config_widget.obj, Project):
                pb_handles = [self.config_widget.handles[key] for key in self.config_widget.handles if key == 'pb']
                pb_handle = pb_handles[0] if pb_handles else None
                if pb_handle is not None:
                    pb_handle.clicked.connect(self.start_project_explorer)
            self.vL_config.addWidget(self.config_widget)

        except Exception as e:
            self.__error_entry__(inspect.currentframe().f_code.co_name, e)

    def update_node(self):
        self.tree.update_item(self.config_widget.obj)
        # self.save_tree()

    def start_project_explorer(self):
        print('Start Project Explorer')


# start GUI ===========================================================================================================
if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = ExampleTree()

    app.setOrganizationName("Remus Engineering")
    app.setOrganizationDomain("remus-engineering.tech")
    app.setApplicationName("Example Tree Template v{}".format(__version__))
    app.setWindowIcon(QIcon(os.path.join(gui.home_path, 'appicon.ico')))
    gui.setWindowTitle('{}'.format(app.applicationName()))
    gui.show()
    sys.exit(app.exec())

