import json
from pathlib import Path

from .columnio import decode, encode, regional
from .contracts import SCHEMA, columns
from .storage import atomic, connect, fingerprint

DDL = """
CREATE TABLE IF NOT EXISTS batches(name TEXT PRIMARY KEY,checksum TEXT NOT NULL,path TEXT);
CREATE TABLE IF NOT EXISTS event_keys(event_id TEXT PRIMARY KEY,batch TEXT NOT NULL REFERENCES batches(name));
CREATE TABLE IF NOT EXISTS versions(id INTEGER PRIMARY KEY,files TEXT NOT NULL,schema_json TEXT NOT NULL);
"""


class CourseTable:
    def __init__(self, root):
        self.root = Path(root)
        self.db = connect(root, DDL)

    def close(self):
        self.db.close()

    def append(self, batch, rows):
        checksum = fingerprint(rows)
        with atomic(self.db):
            old = self.db.execute('SELECT checksum FROM batches WHERE name=?', (batch,)).fetchone()
            if old:
                if old[0] != checksum:
                    raise ValueError("批次内容冲突")
                return False
            path = encode(self.root / 'columns', rows)
            self.db.execute('INSERT INTO batches VALUES(?,?,?)', (batch,checksum,path))
            for row in rows:
                self.db.execute('INSERT INTO event_keys VALUES(?,?)', (row['event_id'],batch))
        return True

    def publish(self):
        with atomic(self.db):
            files = [row[0] for row in self.db.execute('SELECT path FROM batches WHERE path IS NOT NULL ORDER BY name')]
            cursor = self.db.execute('INSERT INTO versions(files,schema_json) VALUES(?,?)', (json.dumps(files),json.dumps(SCHEMA)))
        return cursor.lastrowid

    def read(self, version):
        row = self.db.execute('SELECT * FROM versions WHERE id=?', (version,)).fetchone()
        if not row:
            raise KeyError(version)
        paths = json.loads(row['files'])
        return {'columns':columns(json.loads(row['schema_json'])),'rows':decode(paths),'regional':regional(paths)}
