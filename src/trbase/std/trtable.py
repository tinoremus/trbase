from dataclasses import dataclass, field
from typing import List
import xlsxwriter
import datetime
import pandas as pd
from trbase.std.trobject import TrObject


@dataclass()
class TrTable(TrObject):
    header: List[str] or List[List[str]]
    data: List[list]
    name: str = field(default='')
    delimiter: str = field(default=' ')
    header_seperator: str = field(default='')

    @property
    def header_rows(self) -> int:
        first_item = self.header[0] if self.header else None
        if first_item is None:
            rows = 0
        elif isinstance(first_item, list):
            rows = len(self.header)
        else:
            rows = 1
        return rows

    @property
    def header_columns(self) -> int:
        first_item = self.header[0] if self.header else None
        if first_item is None:
            cols = 0
        elif isinstance(first_item, list):
            cols = len(first_item)
        else:
            cols = len(self.header)
        return cols

    @property
    def __str_header__(self) -> List[str] or List[List[str]]:
        if self.header_rows > 1:
            str_header = list()
            for row in self.header:
                str_row = [str(h) for h in row]
                str_header.append(str_row)
        else:
            str_header = [str(h) for h in self.header]
        return str_header

    @property
    def header_single_row(self) -> List[str]:
        if self.header_rows == 1:
            return self.header
        elif self.header_rows > 1:
            single_header = []
            for cid in range(self.header_columns):
                items = [row[cid] for row in self.__str_header__]
                single_header.append(self.header_seperator.join(items))
            return single_header
        else:
            return self.header

    @property
    def data_rows(self):
        return len(self.data)

    @property
    def data_columns(self):
        return len(self.data[0]) if self.data else 0

    @property
    def __max_column_widths__(self) -> List[int]:
        def _get_max_width_(al: list, bl: list) -> list:
            return [max(a, len(str(b))) for a, b in zip(al, bl)]

        max_column_widths = [-1] * self.header_columns
        if self.header_rows == 1:
            max_column_widths = _get_max_width_(max_column_widths, self.header)
        elif self.header_rows > 1:
            for header_row in self.header:
                max_column_widths = _get_max_width_(max_column_widths, header_row)
        for data_row in self.data:
            max_column_widths = _get_max_width_(max_column_widths, data_row)
        return max_column_widths

    def sort_by_column_number(self, cid: int, reverse: bool = False):
        if not isinstance(cid, int):
            return
        if 0 > cid > self.data_columns:
            return
        self.data.sort(key=lambda x: (x[cid]), reverse=reverse)

    def sort_by_column_name(self, cname: str, reverse: bool = False):
        if not isinstance(cname, str):
            return
        if cname not in self.header:
            return
        cid = self.header.index(cname)
        self.sort_by_column_number(cid, reverse=reverse)

    def write_to_xlsx(self, file_path: str, sheet: str, **kwargs):
        workbook = xlsxwriter.Workbook(file_path)
        worksheet = workbook.add_worksheet(sheet)
        self.write_to_worksheet(workbook, worksheet, **kwargs)
        workbook.close()

    def write_to_worksheet(self, wb: xlsxwriter.Workbook, ws: xlsxwriter.workbook.Worksheet, **kwargs):
        def write_row(_row: list, _rid: int, _fmt):
            for _cid, _cell in enumerate(_row):
                ws.write(_rid, _cid, str(_cell), _fmt)
            return _rid + 1

        header_text_wrap = kwargs['text_wrap'] if 'text_wrap' in kwargs else False
        header_bold = kwargs['header_bold'] if 'header_bold' in kwargs else True

        # FORMATS
        header_format = wb.add_format()
        header_format.set_text_wrap() if header_text_wrap else None
        header_format.set_bold() if header_bold else None

        currency_format = wb.add_format({'num_format': '$0.00'})
        float_format = wb.add_format({'num_format': '0.00'})
        int_format = wb.add_format({'num_format': '0'})
        datetime_format = wb.add_format({'num_format': 'dd/mm/yyyy hh:mm:ss'})
        time_format = wb.add_format({'num_format': 'hh:mm:ss'})

        rid = 0
        # WRITE HEADER
        if self.header_rows == 1:
            rid = write_row(self.header, rid, header_format)
        elif self.header_rows > 1:
            for hrow in self.header:
                rid = write_row(hrow, rid, header_format)

        # WRITE DATA
        for row_id, row in enumerate(self.data, start=rid):
            for col_id, cell in enumerate(row):
                if isinstance(cell, list):
                    export_list = [str(item) for item in cell]
                    if cell:
                        ws.write(row_id, col_id, '\n'.join(export_list))
                else:
                    if isinstance(cell, str):
                        if cell.strip().startswith('$'):
                            value = float(cell.replace('$', '').replace(' ', ''))
                            ws.write(row_id, col_id, value, int_format)
                        else:
                            ws.write(row_id, col_id, cell)
                    elif isinstance(cell, int):
                        ws.write(row_id, col_id, cell, int_format)
                    elif isinstance(cell, float):
                        ws.write(row_id, col_id, cell, float_format)
                    elif isinstance(cell, datetime.datetime):
                        ws.write(row_id, col_id, cell, datetime_format)
                    elif isinstance(cell, datetime.timedelta):
                        ws.write(row_id, col_id, cell, time_format)
                    else:
                        ws.write(row_id, col_id, cell)

    def to_html(self, **kwargs):
        classes = kwargs['classes'] if 'classes' in kwargs else 'table'
        border_width = kwargs['border_width'] if 'border_width' in kwargs else 1
        show_header = kwargs['show_header'] if 'show_header' in kwargs else True
        show_index = kwargs['show_index'] if 'show_index' in kwargs else False
        justify = kwargs['justify'] if 'justify' in kwargs else 'center'

        _df = pd.DataFrame(self.data, columns=self.header)
        table_html = _df.to_html(
            classes=classes,
            border=border_width,
            header=show_header,
            index=show_index,
            justify=justify,
        )
        return table_html

    def show_table_info(self, cmd_output=False, **kwargs) -> None or list:
        print_offset = kwargs['print_offset'] if 'print_offset' in kwargs else ''
        print_string = kwargs['print_string'] if 'print_string' in kwargs else '  {:20}: {}'
        print_string = print_offset + print_string

        info = list()
        info.append('TABLE INFO:')
        info.append(print_string.format('Header Rows', self.header_rows))
        info.append(print_string.format('Header Columns', self.header_columns))
        info.append(print_string.format('Data Rows', self.data_rows))
        info.append(print_string.format('Data Columns', self.data_columns))
        info.append('')
        info.append(print_string.format('Column Widths', self.__max_column_widths__))
        info.append('')

        if cmd_output:
            for line in info:
                print(line)
        else:
            return info

    def __get_formatted_row_string__(self, row: list, fit_columns: bool, padding: int) -> str:
        pad = ' ' * padding if padding else ''
        if fit_columns:
            items = [('{:' + f'{fmt}' + '}').format(cell) for fmt, cell in zip(self.__max_column_widths__, row)]
            items = [pad + item + pad for item in items]
            row_string = self.delimiter.join([str(item) for item in items])
        else:
            row_string = self.delimiter.join([str(item) for item in row])
        return row_string

    def show(self, cmd_output: bool = False, fit_columns: bool = True, padding: int = 1):

        info = list()
        # WRITE HEADER
        if self.header_rows == 1:
            info.append(self.__get_formatted_row_string__(row=self.header, fit_columns=fit_columns, padding=padding))
        else:
            for header_row in self.header:
                info.append(self.__get_formatted_row_string__(row=header_row, fit_columns=fit_columns, padding=padding))
        # SEPARATOR
        if info:
            info.append('-' * len(info[-1]))
        # WRITE DATA
        for data_row in self.data:
            info.append(self.__get_formatted_row_string__(row=data_row, fit_columns=fit_columns, padding=padding))

        if cmd_output:
            for line in info:
                print(line)
        else:
            return info


# TEST ================================================================================================================
if __name__ == '__main__':
    header = [['', 'A', 'B', 'C', 'D', 'E'], ['', 1, 2, 3, 4, 5]]
    data = [
        ['Age', 29, 35, 17, 19, 11],
        ['Height', 165, 174, 164, 167, 60],
    ]
    table = TrTable(header=header, data=data, name='Example', delimiter='')
    # table.show_table_info(True)
    table.show(True, fit_columns=True)
    table.header_seperator = '-'
    print(table.header_single_row)
