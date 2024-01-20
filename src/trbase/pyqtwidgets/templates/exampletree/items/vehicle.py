from dataclasses import dataclass
from trbase.pyqtwidgets.configwidget.configwidgetitem import ConfigWidgetItem


@dataclass()
class Vehicle(ConfigWidgetItem):

    @staticmethod
    def get_default():
        return Vehicle(0, 'New Vehicle', '', None, [], 0)
