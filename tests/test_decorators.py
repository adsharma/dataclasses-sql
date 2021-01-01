import os
import unittest
from collections import OrderedDict
from dataclasses import dataclass, field

os.environ["SQLA_ENGINE"] = "sqlite://"  # Use in-memory
from dataclasses_sql.decorators import sql


@dataclass
@sql
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
        kia_ceed.mileage = 100
        self.assertEqual(True, kia_ceed._dirty)
        # This can help with more efficient upsert where only modified
        # columns are written
        self.assertEqual(
            OrderedDict({"mileage": 100}).items(), OrderedDict.items(kia_ceed)
        )
        kia_ceed.save()
        kia_ceed = Car.get(car._rowid)
        self.assertEqual(100, kia_ceed.mileage)
