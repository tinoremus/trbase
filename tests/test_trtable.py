from trbase.std.trtable import TrTable


def test_header():
    data = []
    table = TrTable(header=[], data=data)
    assert len(table.header) == 0
    assert table.header_rows == 0
    assert table.header_columns == 0
    table = TrTable(header=['', 'A', 'B', 'C', 'D', 'E'], data=data)
    assert len(table.header) == 6
    assert table.header_rows == 1
    assert table.header_columns == 6
    table = TrTable(header=[['', 'A', 'B', 'C', 'D', 'E'], ['', 1, 2, 3, 4, 5]], data=data)
    assert len(table.header) == 2
    assert len(table.header[0]) == 6
    assert len(table.header[1]) == 6
    assert table.header_rows == 2
    assert table.header_columns == 6


def test_data():
    header = []
    table = TrTable(header=header, data=[['Age', 29, 35, 17, 19, 11], ['Height', 165, 174, 164, 167, 60]])
    assert len(table.data) == 2
    assert len(table.data[0]) == 6
    assert len(table.data[1]) == 6
    assert table.data_rows == 2
    assert table.data_columns == 6


def test_name():
    header = []
    data = []
    table = TrTable(header=header, data=data)
    assert table.name == ''
    table = TrTable(header=header, data=data, name='')
    assert table.name == ''
    table = TrTable(header=header, data=data, name='Test Table')
    assert table.name == 'Test Table'


