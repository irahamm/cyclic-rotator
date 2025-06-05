# unify
def unify_doubles(loaded_json: list):
    # (json is a list of dicts)
    # alright, this function probably should be here because we probably don't want many calculations
    # in the front end
    # AND
    # it doesn't return json.
    # it returns only the drum vals
    # after they have been unified
    # so they can be understood by the second html easily and simply
    sub_div = int(loaded_json[0]['subdivision'])
    output = ['']*sub_div
    for i in range(sub_div):
        for item in loaded_json:
            if round(float(item['time']), 10) == round(i/sub_div, 10):
                output[round(float(item['time'])*sub_div)] += item['drum']

        if output[i] == "":
            output[i] = "rest"
    return output


# rotate
def rotate(lst: list):
    output = []
    for i in range(len(lst)):
        output.append(lst[i:]+lst[:i])
    return output


def process_note_positions(loaded_json: list):
    """this function adds rests where the user did not input notes"""
    # write this there:
    sub_div = int(loaded_json[0]['subdivision'])
    note_positions = [round(float(val['time']), 10) for val in loaded_json]
    print(f"note positions:{note_positions}")
    # json is a list of dicts
    # these dicts will have time, drum, and subdivision keys
    for i in range(int(sub_div)):
        if i==0:
            if 0 not in note_positions:
                loaded_json.append({'time': '0', 'drum': 'rest', 'subdivision': str(sub_div)})
        elif round(i/sub_div, 10) not in note_positions:
            print(i, i/sub_div)
            loaded_json.append({'time': str(i/sub_div), 'drum': 'rest', 'subdivision': str(sub_div)})

    return sorted(loaded_json, key= lambda x: x['time'])