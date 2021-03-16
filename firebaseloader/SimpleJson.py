class JsonFieldError(Exception):
    def __init__(self, err_msg, offending_field, err_type = ""):
        super().__init__(err_msg)
        self.offending_field = offending_field
        self.error_type = err_type

def get_json_value(json_obj, field_name):
    if field_name in json_obj:
        value = json_obj[field_name]
        if not isinstance(value, str):
            raise JsonFieldError(f'Error: {field_name} is not string.', field_name, "not a string")
        if value == '':
            raise JsonFieldError(f'Error: {field_name} is empty.', field_name, "empty")
    else:
        raise JsonFieldError(f'Error: {field_name} is missing.', field_name, "missing")
    return value

def get_dict_value(field_path, dict):
    paths = field_path.strip().replace('\\', '/').split('/')
    paths = [path for path in paths if path != '']
    d = dict
    try:
        for p in paths:
            if p in d:
                d = d[p]
            else:
                return None
    except:
        return None
    return d
