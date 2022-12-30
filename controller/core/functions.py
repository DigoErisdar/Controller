def aggregate_wrapper(name: str, *fields):
    if not fields:
        fields = ['*']
    return f'{name}({",".join(fields)})'


def count(*fields):
    return aggregate_wrapper('count', *fields)
