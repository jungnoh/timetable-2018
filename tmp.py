def make_random_pairs(length, count, tc=None):
    tc = tc or [ [CPD*i, CPD*(i+1)] for i in range(5)]
    drawbox = []
    for i in range(len(tc)):
        tc[i][1] = tc[i][1]-length
        diff = tc[i][1] - tc[i][0]
        drawbox.extend([ i for k in range(diff+1)])

    choices = []
    for i in range(count):
        choices.append(drawbox_random(tc, drawbox))
    
    while True:
        wrong = False
        for i in range(count):
            for j in range(i):
                if check_overlapping(choices[i], choices[j], length):
                    wrong = True
                    break
            if(wrong):
                del(choices[i])
                choices.append(drawbox_random(tc, drawbox))
                break
        if not wrong:
            break
    
    return sorted(choices)

def make_group_pairs_single(data):
    copy = data["copy"]
    groups = data["group"]

    teacher_chk = {}
    room_chk = {}
    time_chk = [[False for i in range(5*CPD)] for j in range(copy)]

    for group in groups:
        if group["room"] not in room_chk:
            room_chk[group["room"]] = [False for i in range(5*CPD)]
        for teacher in group["teacher"]:
            if teacher not in teacher_chk:
                teacher_chk[teacher] = [False for i in range(5*CPD)]
    
    while True:
        ret = []
        error = False

        teacher_chk = {}
        room_chk = {}
        time_chk = [[False for i in range(5)] for j in range(copy)]

        for group in groups:
            if group["room"] not in room_chk:
                room_chk[group["room"]] = [False for i in range(5*CPD)]
            for teacher in group["teacher"]:
                if teacher not in teacher_chk:
                    teacher_chk[teacher] = [False for i in range(5*CPD)]

        for group in groups:
            mytc = group["timeConstraints"] if "timeConstraints" in group else None
            ret.append(make_random_pairs(group["len"],copy,tc=mytc))
            index = 0
            for item in ret[-1]:
                if time_chk[index][int(item/CPD)] is True:
                    error = True
                    break
                else:
                    time_chk[index][int(item/CPD)] = True
                for i in range(item, item+group["len"]):
                    if room_chk[group["room"]][i] is True:
                        error = True
                        break
                    else:
                        room_chk[group["room"]][i] = True
                for tea in group["teacher"]:
                    for i in range(item, item+group["len"]):
                        if teacher_chk[tea][i] is True:
                            error = True
                            break
                        else:
                            teacher_chk[tea][i] = True
                    if error is True:
                        break
                index += 1
            if error is True:
                break
        if not error:
            print("done")
            return sorted([ [ ret[i][j] for i in range(len(groups)) ] for j in range(copy)])

def make_group_pairs(data):
    return make_group_pairs_single(data)