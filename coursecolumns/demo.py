from .tables import CourseTable


def run(root):
    table = CourseTable(root)
    try:
        table.append('观看批次A', [
            {'event_id':'E1','campus':{'name':'一校区','region':'东'},'seconds':120},
            {'event_id':'E2','campus':{'name':'二校区','region':'西'},'seconds':90}])
        return table.read(table.publish())
    finally:
        table.close()
