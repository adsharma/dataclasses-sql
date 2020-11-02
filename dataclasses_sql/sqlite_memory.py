import sqlalchemy

# Connect to database
def sqlite_memory_init():
    engine = sqlalchemy.create_engine("sqlite:///:memory:")
    metadata = sqlalchemy.MetaData(engine)
    metadata.reflect()
    return (engine, metadata)
