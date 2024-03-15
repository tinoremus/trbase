from trbase.std.trdataclass import TrDataClass
from dataclasses import dataclass


@dataclass()
class TestDataClass(TrDataClass):
    name: str
    value: int


tdc = TestDataClass(name='Horst', value=23)
TestDataClass.__test__ = False


def test_trdataclass():
    assert tdc.header == ['name', 'value']
    assert tdc.row == ['Horst', 23]
    assert tdc.to_dict() == {'name': 'Horst', 'value': 23}
