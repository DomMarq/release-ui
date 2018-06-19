#--------Helper Functions to be used for sorting and filtering-------#
import datetime


# Filters by all of the criteria shown below, returns an array of filtered releases
def filter(data, state, label, start_date, end_date, datetype):

    # convert variables from unix type to something usable
    state = int(state)
    start_date = int(start_date)
    end_date = int(end_date)

    filtered = []

    # Validate end_date value
    if end_date <= 0:
        end_date = (datetime.datetime.now()-datetime.datetime(1970,1,1)).total_seconds()

    for item in data.items():
        if item[1][datetype] >= start_date and item[1][datetype] <= end_date:
            if item[1]['state'] == state or state == 0:
                if label != 'null':
                    for l in item[1]['labels']:
                        if l == label:
                            filtered.append(item[1])
                else:
                    filtered.append(item[1])

    return filtered


# sorts 'unsorted' according to 'sort_method'. See https://docs.google.com/document/d/1JDD_NX2XVL7yqYcfFOqkef1FKv98nrlRFJ0OpSZprMU/ for enumerations
def sort(unsorted, sort_method):
    sort_method = int(sort_method)
    if sort_method == 1:
        result = sorted(unsorted, key=lambda k: k['name'], reverse=True)
    elif sort_method == 2:
        result = sorted(unsorted, key=lambda k: k['name'])
    elif sort_method == 3:
        result = sorted(unsorted, key=lambda k: k['started'], reverse=True)
    elif sort_method == 4:
        result = sorted(unsorted, key=lambda k: k['started'])
    elif sort_method == 5:
        result = sorted(unsorted, key=lambda k: k['last_modified'], reverse=True)
    elif sort_method == 6:
        result = sorted(unsorted, key=lambda k: k['last_modified'])
    elif sort_method == 7:
        result = sorted(unsorted, key=lambda k: k['last_active_task'], reverse=True)
    elif sort_method == 8:
        result = sorted(unsorted, key=lambda k: k['last_active_task'])
    return result