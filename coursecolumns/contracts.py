SCHEMA = {'event_id':'string','campus':{'name':'string','region':'string'},'seconds':'integer'}


def validate(value, schema=SCHEMA, prefix=''):
    if not isinstance(value, dict) or set(value) != set(schema):
        raise ValueError(f"{prefix or '记录'}字段不符合已登记结构")
    result = {}
    for key, kind in schema.items():
        item = value[key]
        path = prefix + key
        if isinstance(kind, dict):
            result[key] = validate(item, kind, path + '.')
        elif kind == 'string':
            if not isinstance(item, str) or not item:
                raise ValueError(f"{path}需要非空文本")
            result[key] = item
        else:
            if not isinstance(item, int) or isinstance(item, bool) or item < 0:
                raise ValueError(f"{path}需要非负整数")
            result[key] = item
    return result


def columns(schema=SCHEMA, prefix=''):
    result = []
    for key, kind in schema.items():
        if isinstance(kind, dict):
            result.extend(columns(kind, prefix + key + '.'))
        else:
            result.append({'path':prefix + key,'type':kind})
    return result
