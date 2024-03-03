import sys
from enum import Enum
from trbase.pyqtwidgets.checkboxgroup.checkboxgroup import ConfigList, ConfigItem
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QApplication
from dataclasses import dataclass
from trbase.std.trtable import TrTable
from trbase.pyqtwidgets.configwidget.templates import Templates
from trbase.pyqtwidgets.dataclasseditwidget.dataclasseditwidget import DataclassEditable
from trbase.pyqtwidgets.dataclasseditwidget.dataclasseditwidget import DataclassEditWidget


def get_editable_example() -> DataclassEditable:
    class HouseType(Enum):
        SINGLE = 1
        DOUBLE = 2
        CONDO = 3
        TOWNHOUSE = 4

    @dataclass()
    class House:
        name: str
        path: str
        file: str
        type: HouseType
        start_date: float
        day_start_datetime: float
        occupants: int
        area: float
        occupied: bool
        people: list
        history: TrTable
        options: ConfigList

    house = House(name='Mine', path=r'path', file='file', type=HouseType.SINGLE,
                  start_date=1173340800.0, day_start_datetime=0.0, occupants=4,
                  area=120.56, occupied=False, people=['Horst', 'Ani', 'kani', 'hu'],
                  options=ConfigList([
                      ConfigItem(name='Solar', state=False),
                      ConfigItem(name='Pool', state=True),
                  ]),
                  history=TrTable(header=['Start Year', 'End Year', 'Names'],
                                  data=[[2018, 2020, 'Us'], [2020, 2022, 'Someone']]))

    house_editable = DataclassEditable(house)
    house_editable.add_editable_value(
        name='name',
        value=house.name,
        template=Templates.LineEdit,
    )
    house_editable.add_editable_value(
        name='file',
        value=house.file,
        template=Templates.LineEditSelectFile,
    )
    house_editable.add_editable_value(
        name='path',
        value=house.path,
        template=Templates.LineEditSelectPath,
    )
    house_editable.add_editable_value(
        name='type',
        value=house.type,
        template=Templates.ComboBox,
        options=HouseType,
    )
    # house_editable.add_editable_value(
    #     name='start_date',
    #     value=house.start_date,
    #     template=Templates.DateEdit
    # )
    house_editable.add_editable_value(
        name='start_date',
        value=house.start_date,
        template=Templates.DateEditTodayButton
    )
    # house_editable.add_editable_value(
    #     name='day_start_datetime',
    #     value=house.day_start_datetime,
    #     template=Templates.DateTimeEdit
    # )
    house_editable.add_editable_value(
        name='day_start_datetime',
        value=house.day_start_datetime,
        template=Templates.DateTimeEditNowButton
    )
    house_editable.add_editable_value(
        name='occupants',
        value=house.occupants,
        template=Templates.SpinBox
    )
    house_editable.add_editable_value(
        name='area',
        value=house.area,
        template=Templates.DoubleSpinBox,
        options=[0, 9999999]
    )
    house_editable.add_editable_value(
        name='occupied',
        value=house.occupied,
        template=Templates.CheckBox
    )
    house_editable.add_editable_value(
        name='',
        value='Push to Start',
        template=Templates.PushButton
    )
    # house_editable.add_editable_value(
    #     name='people',
    #     value=house.people,
    #     template=Templates.ListStatic
    # )
    house_editable.add_editable_value(
        name='people',
        value=house.people,
        template=Templates.ListEdit
    )
    # house_editable.add_editable_value(
    #     name='history',
    #     value=house.history,
    #     template=Templates.TableStatic
    # )
    house_editable.add_editable_value(
        name='options',
        value=house.options,
        template=Templates.CheckBoxGroup,
        options={'rows': 1, 'columns': 3}
    )
    house_editable.add_editable_value(
        name='history',
        value=house.history,
        template=Templates.TableEdit
    )
    return house_editable


class ExampleWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(300, 300)
        self.setWindowTitle("TreeItem Widget")

        layout = QHBoxLayout(self)
        self.setLayout(layout)

        dew = DataclassEditWidget(get_editable_example())
        layout.addWidget(dew)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = ExampleWidget()
    gui.show()
    sys.exit(app.exec())
