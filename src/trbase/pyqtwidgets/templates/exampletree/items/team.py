from dataclasses import dataclass, field
from trbase.pyqtwidgets.configwidget.configwidgetitem import ConfigWidgetItem, Templates
from trbase.std.trtable import TrTable


@dataclass()
class Team(ConfigWidgetItem):
    my_table: TrTable = field(
        default=None,
        metadata={'render': True, 'position': 26, 'editable': True, 'template': Templates.TableEdit})

    @staticmethod
    def get_default():
        return Team(0, 'New Team', '', None, [], 0)
