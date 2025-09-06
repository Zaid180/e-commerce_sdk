import shelve
from contextlib import contextmanager

DB_PATH = 'ecommerce_db'

@contextmanager
def get_db():
    db = shelve.open(DB_PATH, writeback=True)
    try:
        yield db
    finally:
        db.close()
