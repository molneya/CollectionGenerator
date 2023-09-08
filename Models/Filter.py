
class Filter:
    comparators = {
        '<=': {
            float: lambda x, y: x < y + 0.005,
            int: lambda x, y: x <= y,
            bool: lambda x, y: False,
            str: lambda x, y: False,
        },
        '>=': {
            float: lambda x, y: x > y - 0.005,
            int: lambda x, y: x >= y,
            bool: lambda x, y: False,
            str: lambda x, y: False,
        },
        '!=': {
            float: lambda x, y: not y - 0.005 < x < y + 0.005,
            int: lambda x, y: x != y,
            bool: lambda x, y: x != y,
            str: lambda x, y: x != y,
        },
        '==': {
            float: lambda x, y: y - 0.005 < x < y + 0.005,
            int: lambda x, y: x == y,
            bool: lambda x, y: x == y,
            str: lambda x, y: x == y, # Exact string search
        },
        '=': {
            float: lambda x, y: y - 0.005 < x < y + 0.005,
            int: lambda x, y: x == y,
            bool: lambda x, y: x == y,
            str: lambda x, y: y in x, # Partial string search
        },
        '<': {
            float: lambda x, y: x < y - 0.005,
            int: lambda x, y: x < y,
            bool: lambda x, y: False,
            str: lambda x, y: False,
        },
        '>': {
            float: lambda x, y: x > y + 0.005,
            int: lambda x, y: x > y,
            bool: lambda x, y: False,
            str: lambda x, y: False,
        },
    }

    @staticmethod
    def convert_status(status: str):
        if status[0] == "u": return 0
        if status[0] == "n": return 1
        if status[0] == "p": return 2
        if status[0] == "x": return 3
        if status[0] == "r": return 4
        if status[0] == "a": return 5
        if status[0] == "q": return 6
        if status[0] == "l": return 7
        return -1

    @staticmethod
    def convert_mode(mode: str):
        if mode[0] == "o": return 0
        if mode[0] == "t": return 1
        if mode[0] == "c": return 2
        if mode[0] == "m": return 3
        return -1

    @staticmethod
    def convert_value(key: str, value: str, type: type):
        if key == "mode":
            return Filter.convert_mode(value)
        if key == "status":
            return Filter.convert_status(value)
        return type(value)

    @staticmethod
    def parse_items(key: str, cmp: str, value: str, model):
        annotations = model.__annotations__
        if key in annotations:
            type = annotations[key]
            # Unsupported type
            if type not in [float, int, bool, str]:
                return lambda x: False
            # Some types use substitutions, like mode and status
            value = Filter.convert_value(key, value, type)
            return lambda x: Filter.comparators[cmp][type](x.__dict__[key], value)
        # No valid key, therefore we cannot possibly filter this
        return lambda x: False

    @staticmethod
    def parse(filter: str, model):
        for cmp in Filter.comparators:
            if cmp in filter:
                key, value = filter.split(cmp, 1)
                return Filter.parse_items(key, cmp, value, model)
        # If no comparator, assume we want to do a search instead of filter
        return lambda x: filter in x.search()
