import tempfile
import unittest


class WorkspaceTest(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory()
        self.directory=self.temporary.name
        self.resources=[]

    def open(self, factory):
        resource=factory(self.directory)
        self.resources.append(resource)
        return resource

    def tearDown(self):
        for resource in reversed(self.resources):
            resource.close()
        self.temporary.cleanup()

from coursecolumns.tables import CourseTable
from coursecolumns.contracts import validate, columns


def view(event='E1', seconds=30):
    return {'event_id':event,'campus':{'name':'一校区','region':'东'},'seconds':seconds}


class Behavior(WorkspaceTest):
    def test_nested_contract(self):
        self.assertEqual(validate(view()), view())
        self.assertIn({'path':'campus.name','type':'string'}, columns())
        with self.assertRaises(ValueError):
            validate(dict(view(), seconds=True))
        with self.assertRaises(ValueError):
            validate(dict(view(), campus={'name':'一校区'}))

    def test_batch_checksum_and_empty(self):
        table = self.open(CourseTable)
        self.assertTrue(table.append('B1', [view()]))
        self.assertFalse(table.append('B1', [view()]))
        with self.assertRaises(ValueError):
            table.append('B1', [view(seconds=31)])
        table.append('empty', [])
        version = table.publish()
        self.assertEqual(len(table.read(version)['rows']), 1)

    def test_duplicate_key_rollback(self):
        table = self.open(CourseTable)
        table.append('B1', [view()])
        import sqlite3
        with self.assertRaises(sqlite3.IntegrityError):
            table.append('B2', [view('E2'),view()])
        self.assertIsNone(table.db.execute("SELECT 1 FROM batches WHERE name='B2'").fetchone())
        self.assertEqual(len(table.read(table.publish())['rows']), 1)

    def test_nested_parquet_and_versions(self):
        table = self.open(CourseTable)
        table.append('B1', [view()])
        first = table.publish()
        table.append('B2', [view('E2', 20)])
        second = table.publish()
        reopened = self.open(CourseTable)
        self.assertEqual(reopened.read(first)['rows'][0]['campus']['name'], '一校区')
        self.assertEqual(reopened.read(second)['regional'][0]['seconds'], 50)
