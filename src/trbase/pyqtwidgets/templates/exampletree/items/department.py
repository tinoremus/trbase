from dataclasses import dataclass
from trbase.pyqtwidgets.configwidget.configwidgetitem import ConfigWidgetItem


@dataclass()
class Department(ConfigWidgetItem):

    @staticmethod
    def get_default():
        return Department(0, 'New Department', '', None, [], 0)
