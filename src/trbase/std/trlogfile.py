from trbase.std.trobject import TrObject
from dataclasses import dataclass, field
import os
import re


@dataclass()
class TrLogFile(TrObject):
    __version__ = 1.0
    path: str
    file: str
    text: str = field(default='')
    list: list = field(default_factory=list)

    def set_path(self, value: str) -> bool:
        if not isinstance(value, str):
            return False
        self.path = value
        return True

    def set_file(self, value: str) -> bool:
        if not isinstance(value, str):
            return False
        self.file = value
        return True

    def load(self):
        source_file = os.path.join(self.path, self.file)
        if not os.path.exists(source_file):
            return
        self.text = str()
        with open(source_file, 'rt', encoding='ISO-8859-1') as h_file:
            self.text = h_file.read()
            self.list = re.split("\n+", self.text)

    def show_file_info(self, cmd_output=False, **kwargs):
        print_offset = kwargs['print_offset'] if 'print_offset' in kwargs else ''
        print_string = kwargs['print_string'] if 'print_string' in kwargs else '{:20}: {}'
        print_string = print_offset + print_string
        info = list()

        info.append(print_string.format('Path', self.path))
        info.append(print_string.format('File', self.file))

        if cmd_output:
            for line in info:
                print(line)
        else:
            return info
