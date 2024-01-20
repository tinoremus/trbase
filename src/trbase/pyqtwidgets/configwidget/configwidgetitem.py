from trbase.pyqtwidgets.configwidget.templates import Templates
from dataclasses import dataclass, field, asdict, astuple
from typing import List


DEFAULT_METADATA = {
    'render': False,
    'position': -1,
    'editable': False,
    'template': None,
    'options': dict(),
}


@dataclass()
class ConfigWidgetItem:
    id: int = field(
        metadata={'render': True, 'position': 0, 'editable': False, 'template': Templates.LineEdit})
    name: str = field(
        metadata={'render': True, 'position': 1, 'editable': True, 'template': Templates.LineEdit})
    description: str = field(
        metadata={'render': True, 'position': 9999, 'editable': True, 'template': Templates.TextEdit})
    parent: int or None = field(
        metadata={'render': False})
    children: List[int] = field(
        metadata={'render': False})
    level: int = field(
        metadata={'render': False})

    @staticmethod
    def get_default():
        pass

    def update_object_from(self, old):
        try:
            for name in old.__dataclass_fields__:
                value = old.__getattribute__(name)
                self.__setattr__(name, value)
        except AttributeError:
            pass

    def get_edit_items(self) -> dict:
        info = dict()
        for name, value in zip(asdict(self), astuple(self)):
            # noinspection PyUnresolvedReferences
            meta = self.__dataclass_fields__[name].metadata
            if not meta['render']:
                continue
            info.update({name: meta})
        return info
