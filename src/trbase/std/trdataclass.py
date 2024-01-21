from dataclasses import dataclass
from dataclasses import astuple, asdict
from typing import List


@dataclass()
class TrDataClass:

    @property
    def header(self) -> List[str]:
        return [item for item in self.__dict__]

    @property
    def row(self) -> List[any]:
        return [self.__getattribute__(name) for name in self.header]

    def to_dict(self) -> dict:
        info = dict()
        for name, value in zip(asdict(self), astuple(self)):
            info.update({name: value})
        return info

    def show(self, cmd_output=False):
        info = list()

        for name, value in zip(asdict(self), astuple(self)):
            info.append('{:25}: {}'.format(name, value))

        if cmd_output:
            for line in info:
                print(line)
        else:
            return info
