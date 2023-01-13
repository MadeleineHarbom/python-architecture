from dataclasses import dataclass
from collections import namedtuple


@dataclass(frozen=True)
class Name:
    first_name: str
    surname: str


@dataclass(frozen=True)
class Money:
    currency: str
    value: int

    def __add__(self, other):
        if other.currency != self.currency:
            raise ValueError(f"Cannot add {self.currency} and {other.currency}")
        return Money(self.currency, self.value + other.value)

    def __sub__(self, other):
        if other.currency != self.currency:
            raise ValueError(f"Cannot subtract {self.currency} and {other.currency}")
        return Money(self.currency, self.value - other.value)

    def __mul__(self, other):
        try:
            return Money(self.currency, self.value * other)
        except:
            raise TypeError


Line = namedtuple('Line', ['sku', 'qty'])


def test_equality():
    assert Money('gbp', 10) == Money('gbp', 10)
    assert Name('Harry', 'Percival') != Name('Bob', 'Gregory')
    assert Line('RED-CHAIR', 5) == Line('RED-CHAIR', 5)
