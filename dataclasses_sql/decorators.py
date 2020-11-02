from .sqlite_memory import sqlite_memory_init
from .insert import insert
from .select import SelectStatementBuilder

# Connect to database. TODO: make this configurable
engine, metadata = sqlite_memory_init()


# Decorators
def sql(cls):
    def post_init(self):
        # Do any initializations here
        pass

    def save(self):
        insert(metadata, self, check_exists=True)

    @classmethod
    def get(cls, idvalue):
        builder = SelectStatementBuilder()
        builder.add_all_columns(cls)
        builder.add_clause(cls, "id", idvalue)
        statement = builder.build()

        with metadata.bind.begin() as conn:
            row = conn.execute(statement).fetchone()
        kwargs = {k: v for k, v in row.items() if k != "id"}
        instance = cls(**kwargs)  # TODO: Figure out how to construct a cls from row
        instance._rowid = row["id"]
        return instance

    extra = {"__post_init__": post_init, "save": save}
    cls = type(cls.__name__, (), {**cls.__dict__, **extra})
    cls.get = get
    return cls
