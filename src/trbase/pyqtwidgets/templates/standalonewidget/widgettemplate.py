__version__ = '0.01'
import os
import sys
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from trbase.pyqtwidgets.trqwidget import TrQWidget
import inspect
try:
    from ui_widget_template import *
except ModuleNotFoundError:
    from .ui_widget_template import *


class ReQWidgetTemplate(TrQWidget, Ui_Form):

    def __init__(self, **kwargs):
        """ initialize class """

        try:
            super().__init__()
            self.setupUi(self)

            if getattr(sys, 'frozen', False):
                self.home_path = os.path.dirname(sys.executable)
            elif __file__:
                self.home_path = os.path.dirname(__file__)

            self.update_log('Starting GUI')

        except Exception as e:
            self.__error_entry__(inspect.currentframe().f_code.co_name, e)

    def connect(self):
        """

        :return:
        """
        try:
            pass
        except Exception as e:
            self.__error_entry__(inspect.currentframe().f_code.co_name, e)


# start GUI ===========================================================================================================
if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = ReQWidgetTemplate()

    app.setOrganizationName("Remus Engineering")
    app.setOrganizationDomain("remus-engineering.tech")
    app.setApplicationName("TRQWidget Base Template v{}".format(__version__))
    app.setWindowIcon(QIcon(os.path.join(gui.home_path, 'appicon.ico')))
    gui.setWindowTitle('{}'.format(app.applicationName()))
    gui.show()
    sys.exit(app.exec())

