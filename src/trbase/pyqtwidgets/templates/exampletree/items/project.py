from dataclasses import dataclass, field
from trbase.pyqtwidgets.configwidget.configwidgetitem import ConfigWidgetItem, Templates
from trbase.pyqtwidgets.checkboxgroup.checkboxgroup import ConfigList
from enum import Enum
import datetime
DEFAULT_DATETIME = datetime.datetime(2000, 1, 1)


class StatusOption(Enum):
    Select = 0
    Active = 1
    InActive = 2


@dataclass()
class Project(ConfigWidgetItem):
    status: StatusOption = field(
        default=StatusOption.Select,
        metadata={'render': True, 'position': 20, 'editable': True, 'template': Templates.ComboBox,
                  'options': StatusOption})
    start_date: float = field(
        default=DEFAULT_DATETIME.timestamp(),
        metadata={'render': True, 'position': 21, 'editable': True, 'template': Templates.DateEdit})
    end_date: float = field(
        default=DEFAULT_DATETIME.timestamp(),
        metadata={'render': True, 'position': 22, 'editable': True, 'template': Templates.DateEditTodayButton})
    timestamp: float = field(
        default=DEFAULT_DATETIME.timestamp(),
        metadata={'render': True, 'position': 23, 'editable': True, 'template': Templates.DateTimeEdit})
    timestamp1: float = field(
        default=DEFAULT_DATETIME.timestamp(),
        metadata={'render': True, 'position': 24, 'editable': True, 'template': Templates.DateTimeEditNowButton})
    path: str = field(
        default='',
        metadata={'render': True, 'position': 25, 'editable': True, 'template': Templates.LineEditSelectPath})
    file: str = field(
        default='',
        metadata={'render': True, 'position': 25, 'editable': True, 'template': Templates.LineEditSelectFile})
    mylist: list = field(
        default=None,
        metadata={'render': True, 'position': 26, 'editable': True, 'template': Templates.ListEdit})
    pb: str = field(
        default='Button',
        metadata={'render': True, 'position': 30, 'editable': True, 'template': Templates.PushButton})
    select_tflite_delegate: ConfigList = field(
        default=ConfigList([]),
        metadata={'render': True, 'position': 27, 'editable': True, 'template': Templates.CheckBoxGroup,
                  'options': {'rows': 1, 'columns': 3}})

    @staticmethod
    def get_default():
        return Project(0, 'New Project', '', None, [], 0, StatusOption.Select,
                       DEFAULT_DATETIME.timestamp(), DEFAULT_DATETIME.timestamp(),
                       DEFAULT_DATETIME.timestamp(), DEFAULT_DATETIME.timestamp(),
                       '', '', [], 'Start Project Explorer', ConfigList([]))
