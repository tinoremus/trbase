from trbase.helper.stringutils import camel_case_to_pythonic


def dict_to_dataclass(js: dict, object_name='DataClassObject', show: bool = True):

    def iter_keys():
        for key in js:
            name = camel_case_to_pythonic(key)
            value: str = js[key]
            dtype = 'str'
            default = "''"
            if value.isnumeric():
                dtype = 'int'
                default = 0
            elif value in ['true', 'false']:
                dtype = 'bool'
                default = False
            else:
                try:
                    float(value)
                    dtype = 'float'
                    default = 0.0
                except ValueError:
                    pass
            yield key, name, dtype, default

    def add_definition():
        for key, name, dtype, _ in iter_keys():
            info.append(f'{spacing}{name}: {dtype}')
        info.append(f'{spacing}')

    def add_instance_maker():
        info.append(f'{spacing}@classmethod')
        info.append(f'{spacing}def from_json(cls, js: dict):')

        # initialize values
        for key, name, dtype, default in iter_keys():
            info.append(f"{spacing}{spacing}{name} = {default}")
        info.append(f'{spacing}')

        # assign values
        info.append(f'{spacing}{spacing}for key in js:')
        first = False
        for key, name, dtype, default in iter_keys():
            if not first:
                info.append(f'{spacing}{spacing}{spacing}if key == "{key}":')
                info.append(f'{spacing}{spacing}{spacing}{spacing}{name} = js[key]')
                first = True
                continue
            info.append(f'{spacing}{spacing}{spacing}elif key == "{key}":')
            info.append(f'{spacing}{spacing}{spacing}{spacing}{name} = js[key]')
        info.append(f'{spacing}{spacing}{spacing}else:')
        info.append(f'{spacing}{spacing}{spacing}{spacing}' + "print(f'Missing key = {key}')")
        info.append(f'{spacing}')

        # create class
        info.append(f"{spacing}{spacing}return cls(")
        for key, name, dtype, default in iter_keys():
            info.append(f"{spacing}{spacing}{spacing}{name}={name},")
        info.append(f"{spacing}{spacing})")

        info.append(f'{spacing}')

    def add_show():
        info.append(f'{spacing}' + "def show(self, cmd_output: bool = True, print_string: str = '{:30}: {}'):")
        info.append(f'{spacing}{spacing}info = list()')
        for key, name, _, _ in iter_keys():
            info.append(f"{spacing}{spacing}info.append(print_string.format('{key}', self.{name}))")

        info.append(f'{spacing}')
        info.append(f'{spacing}{spacing}if cmd_output:')
        info.append(f'{spacing}{spacing}{spacing}for line in info:')
        info.append(f'{spacing}{spacing}{spacing}{spacing}print(line)')
        info.append(f'{spacing}{spacing}else:')
        info.append(f'{spacing}{spacing}{spacing}return info')
        info.append(f'{spacing}{spacing}')

    spacing = '    '
    info = list()
    info.append('@dataclass()')
    info.append(f'class {object_name}:')
    add_definition()
    add_instance_maker()
    add_show()
    info.append('')

    if show:
        for line in info:
            print(line)
    else:
        return info
