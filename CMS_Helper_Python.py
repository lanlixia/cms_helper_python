import json

def add_newlines(input):
    # split by space
    # count up to 110 characters, then insert newline
    # then rejoin string with spaces
    inp = input.split(" ")
    count = 0

    for i in range(0, len(inp)):
        c = len(inp[i])
        count += 1
        if count + c > 110:
            inp[i - 1] += "\\n"
            count = c
            pass
        else:
            count += c
    
    input = " ".join(inp).replace("\\n ", "\\n").strip()
    return input


def assume_char(input):
    pos = "Left"
    name = ""

    if "_R" in input:
        pos = "Right"
    elif "_C" in input:
        pos = "Center"

    if "Shur" in input:
        name = "Shur"
    elif "Rey" in input:
        name = "Reynald"
    elif "Marl" in input:
        name = "Marlsanna"

    return pos, name


def to_json():
    # init
    filename = 'prologue.txt'
    json_filename = 'prologue.json'

    """ VALIDATION - may read from files in the future """
    # asset validation
    #valid_names = ['Vurg', 'Other Vurg']
    #valid_sprites = ['SpriteVurgSNC', 'SpriteVurgSNB']
    #valid_backgrounds = ['BackgroundCity', 'BackgroundPurple']

    # enum validation
    valid_spots = ['Left', 'Center', 'Right']
    valid_page_types = ['Start', 'Middle', 'End']

    # field names/defaults
    map_names = ['init', 'choices', 'prompts']
    fields = ['mPageNum', 'mName', 'mText', 'mSpriteName', 'mSpriteSpot', 'mBackgroundName', 'mPageType'] # implicit boolChoices
    defaults = ['-99', 'NAME', 'TEXT', 'SpriteVurgSNC', 'Left', 'BackgroundCity', 'Middle']

    # declarations
    book = dict()
    lines = []

    # read file into string list of lines
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # parse each line into a page for book
    for l in lines:
        l = l.strip()
        if l == "":
            continue
        # split each line into elements
        objs = [o.strip() for o in l.split("|")]
        if len(objs) < len(fields):
            objs.extend(['']  * (len(fields) - len(objs)))

        # assign elements to book
        book[objs[0]] = {'init':{}, 'choices':{}, 'prompts':{}}
        for o in range(0, len(fields)):
            if o < 3:
                # required fields
                objs[o] = objs[o].replace("\\n", "\n")
                book[objs[0]]['init'][fields[o]] = objs[o]
            else:
                # default assumptions
                if objs[o] == '':
                    book[objs[0]]['init'][fields[o]] = defaults[o]
                else:
                    book[objs[0]]['init'][fields[o]] = objs[o]
    
        # if there are choices
        if len(objs) > 7 and objs[7] != '':
            choices = objs[7].split(';')
            for c in choices:
                if c == "":
                    continue
                b = c.split('->')  # d = [choice, page]
                e = b[0].split('$')  # e = [choice, stat_changes]
                d = e[0].split('@') # d = [choice, conditions]
                book[objs[0]][map_names[1]][d[0]] = {}
                book[objs[0]][map_names[1]][d[0]]["Default"] = {}
                book[objs[0]][map_names[1]][d[0]]["Default"]["Changes"] = {}
                book[objs[0]][map_names[1]][d[0]]["Default"]["Changes"]["Page"] = b[1]
                # if there are conditions
                if len(d) > 1:
                    book[objs[0]][map_names[1]][d[0]]["Conditions"] = {}
                    book[objs[0]][map_names[1]][d[0]]["Passed"] = {}
                    book[objs[0]][map_names[1]][d[0]]["Passed"]["Changes"] = {}
                    d[1] = d[1][1:-1]  # removes { }
                    f = d[1].split(')') # [conditions, changes, success page]
                    f[0] = f[0][1:]
                    # changes for success condition
                    if len(f) > 2: 
                        f[1] = f[1][1:]
                        stats = f[1].split(',')
                        for s in stats:
                            change = s.split("]")
                            change[0] = (change[0] + ']').strip()
                            book[objs[0]][map_names[1]][d[0]]["Passed"]["Changes"][change[0]] = change[1].strip()
                        book[objs[0]][map_names[1]][d[0]]["Passed"]["Changes"]["Page"] = f[2].split("=>")[1]
                    else:
                        book[objs[0]][map_names[1]][d[0]]["Passed"]["Changes"]["Page"] = f[1].split("=>")[1]
                    # splitting conditions
                    conds = f[0].split(',')
                    for g in conds:
                        cond = g.split("]")
                        cond[0] = (cond[0] + ']').strip()
                        book[objs[0]][map_names[1]][d[0]]["Conditions"][cond[0]] = cond[1].strip()

                # if there are stat changes for default condition
                if len(e) > 1:
                    e[1] = e[1][1:-1]  # removes { }
                    stats = e[1].split(',')
                    for s in stats:
                        change = s.split("]")
                        change[0] = (change[0] + ']').strip()
                        book[objs[0]][map_names[1]][d[0]]["Default"]["Changes"][change[0]] = change[1].strip()
        else:
            if book[objs[0]]['init']['mPageType'] == 'End':
                # if end, then no next; replace with next chapter in the future
                pass
            elif book[objs[0]]['init']['mPageType'] == 'Start' or book[objs[0]]['init']['mPageType'] == 'Middle':
                # else if start or middle, assume next page
                book[objs[0]][map_names[1]]['Next'] = {}
                book[objs[0]][map_names[1]]['Next']["Default"] = {}
                book[objs[0]][map_names[1]]['Next']["Default"]["Changes"] = {}
                book[objs[0]][map_names[1]]['Next']["Default"]["Changes"]["Page"] = str(int(objs[0]) + 1)

        # if there are text input prompts
        if len(objs) > 8 and objs[8] != '':
            p = objs[8].split('->')
            book[objs[0]][map_names[2]][p[0]] = p[1]

    # outputting to json and print to check
    json_object = json.dumps(book, indent = 4) 
    with open(json_filename, "w") as outfile:
        json.dump(book, outfile)
    #print(json_object)


def to_txt():
    # file init
    script = ""
    with open("script.txt", 'r', encoding='utf-8') as f:
        script = f.read()

    # processing init
    bg = "BackgroundBlack"
    input = [x.strip(" ").replace("…", "...").replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"') for x in script.strip().split("\n")]
    filename = "prologue.txt"
    #00|Vurg|Page 0\n"Welcome to the engine test. Hit space or click 'Next' to advance."|SpriteVurgSNC|Left|BackgroundCity|Start
    #["BackgroundTempleHall", "BackgroundTemplePrayerRoom", "BackgroundTempleRoof", "BackgroundKeepBedroom", "BackgroundKeepTrainingHall", "BackgroundChapelSanitarium", "BackgroundBlack"]

    with open(filename, 'w', encoding='utf-8') as f:
        for i in range(0, len(input)):
            in_str = input[i]
            # handling BG change
            if "BG=" in input[i]:
                in_str = input[i].split("BG=")[0]
                bg = input[i].split("BG=")[1]
            n_str = "| |" # display name
            sp_str = "|SpriteNarrator|Left|" # sprite file + position
            ch_str = "|" # choices
            p_str = "|" # prompts

            pt_str = "|Middle" # page type
            if i == 0:
                pt_str = "|Start"
                
            # handling name/sprite/pos
            if ":" in input[i]:
                in_str = in_str.split(":")[1]
                s = input[i].split(":")[0]
                
                if "MAR" in s:
                    n_str = "|Marlsanna|"
                    sp_str = "|SpriteMarl"
                elif "REY" in s:
                    n_str = "|Reynald|"
                    sp_str = "|SpriteRey"
                elif "SHU" in s:
                    n_str = "|Shur|"
                    sp_str = "|SpriteShur"

                if "_R" in s:
                    sp_str += "Right|Right|"
                elif "_L" in s:
                    sp_str += "Left|Left|"
                elif "_C" in s:
                    sp_str += "Center|Center|"

                if "?" in s:
                    n_str = "|?|"
                if "_ND" in s:
                    n_str = "| |"
                if s[0] == '[' and s[-1] == ']':
                    n_str = "|" + s + "|"
            # handling choices
            if "CH=" in input[i]:
                #print("CH=", input[i])
                ch_l = in_str.split("CH=")[1].split("|")
                in_str = in_str.split("CH=")[0]
                for c in ch_l:
                    if "->" in c:
                       ch_str += (c + ";")
                    else:
                       ch_str += (c + "->" + str(i + 1) + ";")
           # handling input prompts
            if "P=" in input[i]:
                #print("P=", input[i])
                p_str += in_str.split("P=")[1]
                in_str = in_str.split("P=")[0]
                
                
            inp = add_newlines(in_str)
            f.write(str(i) + n_str + inp + sp_str + bg + pt_str + ch_str + p_str + "\n")


def adjust_num(adjust, start=0):
    script = ""
    with open("raw.txt", 'r', encoding='utf-8') as f:
        script = f.read()
    
    x = script.split("\n")
    x = x[start:]
    new_script = ""
    for u in x:
        o = u.split("->")
        for i in o:
            if i.isnumeric():
                i = str(int(i) + adjust)
            if i != o[0]:
                new_script += "->"
            new_script += i
        if u != x[-1]:
            new_script += "\n"
        
    with open("script.txt", 'w', encoding='utf-8') as f:
        f.write(new_script)


#adjust_num(3)
to_txt()
to_json()