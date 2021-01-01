import sqlalchemy

# Connect to database
def sqlite_engine_init(engine_url: str):
    engine = sqlalchemy.create_engine(engine_url)
    metadata = sqlalchemy.MetaData(engine)
    metadata.reflect()
    return (engine, metadata)
