import configparser
import json
import math
import random
import time

config = configparser.ConfigParser()
config.read('settings.ini')

CPD = int(config.get('Config', 'cpd'))

def check_overlapping(t1, t2, l1, l2):
    # Okay if two times are different days
    if int(t1/CPD) != int(t2/CPD):
        return False
    if(t1>t2):
        t1,t2 = t2,t1
        l1,l2 = l2,l1
    return True if t1+l1>t2 else False

def drawbox_random(drawbox, length, tc):
    tc_choice = random.choice(drawbox)
    return random.choice(range(tc[tc_choice][0],tc[tc_choice][1]-length+1))

def make_drawbox(length, tc=None):
    drawbox = []
    for i in range(len(tc)):
        diff = tc[i][1] - length - tc[i][0] + 1
        drawbox.extend([ i for k in range(diff+1)])
    return drawbox
    
def fix_tc(groups):
    for i in range(len(groups)):
        if "tc" not in groups[i].keys():
            groups[i]["tc"] = [[CPD*i, CPD*(i+1)] for i in range(5)]

def init_checks(groups):
    teacher_chk = {}
    room_chk = {}

    for group in groups:
        if group["room"] not in room_chk:
            room_chk[group["room"]] = [False for i in range(5*CPD)]
        for teacher in group["teacher"]:
            if teacher not in teacher_chk:
                teacher_chk[teacher] = [False for i in range(5*CPD)]
    
    return teacher_chk, room_chk

def build_group(groups):
    fix_tc(groups)

    boxes = [
        make_drawbox(group["len"], group["tc"]) for group in groups
    ]
    
    while(True):
        error = False
        ret= []
        for i in range(len(groups)):
            choice = drawbox_random(boxes[i], groups[i]["len"], tc = groups[i]["tc"])
            for j in range(i):
                if int(ret[j]/CPD) == int(choice/CPD):
                    error = True
                    break
            if error is True:
                break
            ret.append(choice)
        if not error:
            return ret
        

def build_choice(data):
    copy = data["copy"]
    groups = data["group"]
    gcnt = len(groups)

    while True:
        error = False
        ret = [build_group(groups) for i in range(copy)]

        teacher_chk, room_chk = init_checks(groups)
        for i in range(copy):
            if error:
                break
            for j in range(gcnt):
                if error:
                    break
                for t in range(ret[i][j], ret[i][j]+groups[j]["len"]):
                    if error:
                        break
                    if room_chk[groups[j]["room"]][t]:
                        error = True
                        break
                    else:
                        room_chk[groups[j]["room"]][t] = True;
                    for tea in groups[j]["teacher"]:
                        if teacher_chk[tea][t]:
                            error = True
                            break
                        else:
                            teacher_chk[tea][t] = True
        if not error:
            return ret

def build_choices(data):
    ret = []
    indexes = []
    index = 0
    for choice in data["choices"]:
        indexes.extend([ index for i in range(int(choice["copy"]))])
        ret.extend(build_choice(choice))
        index += 1
    
    return {
        "times": ret,
        "index": indexes
    }

def build_gene_raw(data):
    ret = {}
    for i in data.keys():
        ret[i] = build_choices(data[i])
    return ret

if __name__ == "__main__":
    data = json.load(open(config.get('Files', 'data'), "r", encoding="utf8"))
    
    sm = 0
    for i in range(100):
        st = time.time()
        build_gene_raw(data["subjects"])
        en = time.time()
        sm += (en-st)
    print("Average time: "+str(sm*10)+"ms")
    
    with open("test_gene.json","w") as f:
        f.write(json.dumps(build_gene_raw(data["subjects"]), indent=4))