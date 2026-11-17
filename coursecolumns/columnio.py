from .contracts import validate
from .parquet import query, write_rows


def encode(directory, rows):
    cleaned = [validate(row) for row in rows]
    identities = [row['event_id'] for row in cleaned]
    if len(identities) != len(set(identities)):
        raise ValueError("同一文件事件键重复")
    return write_rows(directory, cleaned)


def decode(paths):
    return query(paths, 'SELECT * FROM payload ORDER BY event_id')


def regional(paths):
    return query(paths, 'SELECT campus.region region,COUNT(*) view_count,SUM(seconds) AS "seconds" FROM payload GROUP BY campus.region ORDER BY region')
