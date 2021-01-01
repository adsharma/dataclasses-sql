import os

from collections import OrderedDict

from .sqlite_memory import sqlite_memory_init
from .sqlite_engine import sqlite_engine_init
from .insert import insert
from .select import SelectStatementBuilder
from .update import update


# Connect to database. TODO: make this configurable
engine, metadata = sqlite_engine_init(os.getenv("SQLA_ENGINE"))


class SQLModel(OrderedDict):
    """Like an OrderedDict, but treats id as a special key for
       equality purposes and hashable (so you can create sets).
    """

    IDKEY = "id"

    def __post_init__(self):
        OrderedDict.__init__(self, {})
        self._fetching = False
        self._dirty = False

    def __lt__(self, other):
        return self[SQLModel.IDKEY] < other[SQLModel.IDKEY]

    def __eq__(self, other):
        if SQLModel.IDKEY in self:
            return self[SQLModel.IDKEY] == other[SQLModel.IDKEY]
        else:
            return dict.__eq__(self, other)

    def __repr__(self):
        return dict.__repr__(self)

    def __hash__(self) -> int:
        if SQLModel.IDKEY in self:
            return hash(self[SQLModel.IDKEY])
        else:
            return 0

    def __setitem__(self, name, value):
        super().__setitem__(name, value)

    def __setattr__(self, name, value):
        if name == "_dirty":
            super().__setattr__(name, value)
            return
        if hasattr(self, "_fetching") and not self._fetching:
            self._dirty = True
            super().clear()
        super().__setattr__(name, value)
        self.__setitem__(name, value)


# Decorators
def sql(cls):
    def post_init(self):
        # TODO: Debug why this is not called on construction
        SQLModel.__post_init__(self)
        # Do any other initializations here

    def save(self):
        if not insert(metadata, self, check_exists=True):
            update(metadata, self)

    @classmethod
    def statement(cls, statement):
        with metadata.bind.begin() as conn:
            rows = conn.execute(statement).fetchall()
        instances = []
        for row in rows:
            kwargs = {k: v for k, v in row.items() if k != "id"}
            # TODO: Figure out how to construct a cls from row
            instance = cls(**kwargs)
            if "id" in row:
                instance._rowid = row["id"]
            instance._fetching = False
            instances.append(instance)
        return instances

    @classmethod
    def get(cls, idvalue):
        builder = SelectStatementBuilder()
        builder.add_all_columns(cls)
        builder.add_clause(cls, "id", idvalue)
        stmt = builder.build()

        return cls.statement(stmt)[0]

    extra = {"__post_init__": post_init, "save": save}
    newcls = type(cls.__name__, (SQLModel,), {**cls.__dict__, **extra})
    newcls.get = get
    newcls.statement = statement
    return newcls
