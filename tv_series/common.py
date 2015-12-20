SEP = ' :: '


def read_list_from_file(file_path, first_column_only=True):
    items = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line[0] == '#':
                    continue
                if SEP not in line:
                    items.append(line)
                    continue
                line_columns = line.split(SEP)
                if first_column_only:
                    items.append(line_columns[0])
                else:
                    items.append(line_columns)
    except FileNotFoundError:
        pass
    return items


def write_list_to_file(file_path, items):
    with open(file_path, 'a') as f:
        for item in items:
            if type(item) == tuple or type(item) == list:
                f.write(SEP.join([str(i) for i in item]))
            else:
                f.write(item)
            f.write('\n')
            f.flush()
