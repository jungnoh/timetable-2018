import json
import configparser
import math
import string
import random
import time
import copy
import pickle
import concurrent.futures
from operator import itemgetter
import create_gen
import inner_gene_loss

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

config = configparser.ConfigParser()
config.read('settings.ini')

CPD = int(config.get('Config', 'cpd'))
GENS = int(config.get('GA', 'gens'))
POP = int(config.get('GA', 'pop'))
CROSS_PROB = float(config.get('GA', 'cross_prob'))
MUT_PROB = float(config.get('GA', 'mut_prob'))
RATIO = float(config.get('GA','ratio'))

def crossover(data, gene1, gene2):
    keys = list(gene1.keys())
    ngene1, ngene2 = copy.deepcopy(gene1), copy.deepcopy(gene2)
    mut = create_gen.build_gene_raw(data["subjects"])

    divs = random.sample(list(range(len(ngene1))), int(random.random()*3)+1)
    divs.append(len(ngene1))

    ind = 1
    while(ind+1 < len(divs)):
        for i in range(divs[ind], divs[ind+1]):
            ngene1[keys[i]], ngene2[keys[i]] = ngene2[keys[i]], ngene1[keys[i]]
        ind += 2
    
    for i in range(len(divs)):
        if random.random() < MUT_PROB:
            ngene1[keys[i]] = mut[keys[i]]

    """
    for key in keys:
        for c in range(len(gene1[key]["times"])):
            if random.random() < CROSS_PROB:
                ngene1[key]["times"][c] = copy.deepcopy(gene2[key]["times"][c])
                ngene2[key]["times"][c] = copy.deepcopy(gene1[key]["times"][c])
            else:
                ngene1[key]["times"][c] = copy.deepcopy(gene1[key]["times"][c])
                ngene2[key]["times"][c] = copy.deepcopy(gene2[key]["times"][c])
            if random.random() < MUT_PROB:
                ngene1[key]["times"][c] = copy.deepcopy(mut_1[key]["times"][c])
            if random.random() < MUT_PROB:
                ngene2[key]["times"][c] = copy.deepcopy(mut_2[key]["times"][c])
    """
    return ngene1, ngene2

def get_choice_info(subjects, gene, subject, choice):
    return subjects[str(subject)]["choices"][gene[str(subject)]["index"][choice]]["group"]

def calc_all_losses(data, gene, parent_generation=1, gene_id=1):
    # V1 Loss
    v1_data = inner_gene_loss.evaluate(data, gene, parent_generation, gene_id)
    v1 = v1_data[0]
    # V2, V3 Loss
    vo = calc_v2_v3_loss(data, gene)

    print("V1 Loss: "+str(v1)+" / V2/V3 Loss: "+str(vo))
    return [v1, vo, vo+v1*RATIO, v1_data[1]]

# v2, v3: 교사, 강의실 시간 겹침
def calc_v2_v3_loss(data, gene):
    teacher_times = { int(key): [False for i in range(CPD*5)] for key in data["teachers"].keys() }
    room_times = { int(key): [False for i in range(5*CPD)] for key in data["rooms"].keys() }

    loss = 0
    subjects = data["subjects"]
    for subject in subjects.keys():
        my_gene = gene[str(subject)]
        for i in range(len(my_gene["index"])):
            times = my_gene["times"][i]
            sub_data = get_choice_info(subjects, gene, subject, i)
            for t in range(len(sub_data)):
                time_now = times[t]
                sub_now = sub_data[t]
                for ti in range(time_now, time_now+sub_now["len"]):
                    if not room_times[sub_now['room']][ti]:
                        room_times[sub_now['room']][ti] = True
                    else:
                        loss += 1
                    for teacher in sub_now['teacher']:
                        if not teacher_times[teacher][ti]:
                            teacher_times[teacher][ti] = True
                        else:
                            loss += 1
    return loss    

def generation(data, genes, gencnt = 1):
    PROCS = 4

    assert(len(genes)%4 == 0)

    ngenes = []

    count = len(genes)
    students = data["students"]
    subjects = data["subjects"]
    # Make children
    for i in range(int(count/2)):
        c1, c2 = crossover(data, genes[2*i], genes[2*i+1])
        ngenes.append(c1)
        ngenes.append(c2)

    for i in range(int(count/4)):
        ngenes.append(create_gen.build_gene_raw(data["subjects"]))

    ngenes.extend(genes[:int(len(genes)/2)])

    executor = concurrent.futures.ProcessPoolExecutor(PROCS)
    futures = [executor.submit(calc_all_losses, data, ngenes[i], gencnt, i) for i in range(len(ngenes))]
    concurrent.futures.wait(futures)

    for i in range(len(ngenes)):
        f = open("logs/"+runID+"-gen"+str(gencnt)+".txt", "a")
        f.write(">>> Gene"+str(i)+" V1 "+str(futures[i].result()[0])+", V2 "+str(futures[i].result()[1])+", Combined "+str(futures[i].result()[2])+"\n")
        f.write(str(futures[i].result()[3])+"\n")
        f.close()

    group_loss = [
        [ngenes[i], futures[i].result()[2]]
        for i in range(len(ngenes))
    ]
    group_loss = sorted(group_loss, key=itemgetter(1))[:count]
    f = open("logs/"+runID+"-gen"+str(gencnt)+".txt", "a")
    f.write("Best Loss "+str(group_loss[0][1])+" / Worst Loss "+str(group_loss[-1][1])+"\n")
    f.close()
    
    # try: 
    with open("logs/"+runID+"-gen"+str(gencnt)+"-best1", 'wb') as f:
        pickle.dump(group_loss[0], f, pickle.HIGHEST_PROTOCOL)
    with open("logs/"+runID+"-gen"+str(gencnt)+"-best2", 'wb') as f:
        pickle.dump(group_loss[1], f, pickle.HIGHEST_PROTOCOL)
    with open("logs/"+runID+"-gen"+str(gencnt)+"-best3", 'wb') as f:
        pickle.dump(group_loss[2], f, pickle.HIGHEST_PROTOCOL)
    print("Best cases saved as logs/"+runID+"-gen"+str(gencnt)+"-best")
    # except:
    #     print("Failed to save best cases")

    return [item[0] for item in group_loss], group_loss[0][1], group_loss[-1][1]

runID = "123123"

if __name__ == "__main__":
    runID = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(8))

    data = json.load(open(config.get('Files', 'data'), "r", encoding="utf8"))
    genes = []

    """
    g1 = create_gen.build_gene_raw(data["subjects"])
    g2 = create_gen.build_gene_raw(data["subjects"])
    print(g1)
    print("===============")
    print(g2)
    print("===============")
    print(calc_v2_v3_loss(data, g1))
    print(calc_v2_v3_loss(data, g2))

    g1, g2 = crossover(data, g1 ,g2)
    print("===============")
    print(g1)
    print("===============")
    print(g2)
    print("===============")
    print(calc_v2_v3_loss(data, g1))
    print(calc_v2_v3_loss(data, g2))
    """

    # Create initial genes
    st = time.time()
    for i in range(POP):
        genes.append(create_gen.build_gene_raw(data["subjects"]))
    en = time.time()
    print("Initial genes created in "+str((en-st)*1000)+"ms")

    losses = []
    for i in range(GENS):
        st = time.time()
        genes, nloss, wloss = generation(data, genes, gencnt=(i+1))
        en = time.time()
        print("Generation "+str(i+1)+" created in "+str((en-st))+"s, Loss "+str(nloss)+" / "+str(wloss))
        losses.append(nloss)


