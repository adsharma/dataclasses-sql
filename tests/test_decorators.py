import unittest

from dataclasses import dataclass, field
from dataclasses_sql.decorators import sql


@sql
@dataclass
class Car:
    brand: str = field(metadata={"key": True})
    model: str = field(metadata={"key": True})
    mileage: float


class TestDecorators(unittest.TestCase):
    def test_sql_decorator(self):
        car = Car("Kia", "Ceed", 15678)
        car.save()
        kia_ceed = Car.get(car._rowid)
        self.assertEqual(car._rowid, kia_ceed._rowid)
        self.assertEqual("Kia", kia_ceed.brand)
        self.assertEqual("Ceed", kia_ceed.model)
        self.assertEqual(15678, kia_ceed.mileage)
