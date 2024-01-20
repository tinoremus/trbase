from dataclasses import dataclass, field
from trbase.pyqtwidgets.configwidget.configwidgetitem import ConfigWidgetItem, Templates
from enum import Enum


class StatusOption(Enum):
    Select = 0
    Active = 1
    InActive = 2


@dataclass()
class Customer(ConfigWidgetItem):
    status: StatusOption = field(
        default=StatusOption.Select,
        metadata={'render': True, 'position': 20, 'editable': True, 'template': Templates.ComboBox,
                  'options': StatusOption})

    @staticmethod
    def get_default():
        return Customer(0, 'New Customer', '', None, [], 0, StatusOption.Select)
