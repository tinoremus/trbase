

class TrObject(object):
    __version__ = 0.1

    def __init__(self):
        super().__init__()

    def show(self, cmd_output=False, **kwargs):
        print_offset = kwargs['print_offset'] if 'print_offset' in kwargs else ''
        print_string = kwargs['print_string'] if 'print_string' in kwargs else '{:20}: {}'
        print_string = print_offset + print_string
        info = list()

        info.append(print_string.format('Class Name', self.__class__.__name__))

        if cmd_output:
            for line in info:
                print(line)
        else:
            return info
