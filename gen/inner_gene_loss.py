import json
import configparser
import math
import random
import string
import time
import concurrent.futures
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from operator import itemgetter

config = configparser.ConfigParser()
config.read('settings.ini')

CPD = int(config.get('Config', 'cpd'))
GENS = int(config.get('InnerGA', 'gens'))
POP = int(config.get('InnerGA', 'pop'))
CROSS_PROB = float(config.get('InnerGA', 'cross_prob'))
MUT_PROB = float(config.get('InnerGA', 'mut_prob'))

def check_overlapping(t1, t2, l1, l2):
    # Okay if two times are different days
    if int(t1/CPD) != int(t2/CPD):
        return False
    if(t1>t2):
        t1,t2 = t2,t1
        l1,l2 = l2,l1
    return True if t1+l1>t2 else False

def create_placement(students, subjects, times):
    sub_students = {}
    choices = {}
    for student in students:
        choices[student] = []
        for cl in students[student]:
            if cl not in sub_students:
                sub_students[cl] = []
            sub_students[cl].append(student)
    for key in sub_students.keys():
        random.shuffle(sub_students[key])
        std_count = subjects[str(key)]["count"]
        choice_count = len(times[str(key)]["times"])
        stds_per_sub = int(std_count/choice_count)
        overflow_cnt = std_count - stds_per_sub * choice_count
        cs = []
        for i in range(overflow_cnt):
            cs.extend([ i for q in range(stds_per_sub+1)])
        for i in range(overflow_cnt, choice_count):
            cs.extend([ i for q in range(stds_per_sub)])
        for i in range(len(cs)):
            choices[sub_students[key][i]].append(cs[i])
    return choices

def get_choice_info(subjects, master_gene, subject, choice):
    return subjects[str(subject)]["choices"][master_gene[str(subject)]["index"][choice]]["group"]

# v1: 학생 시간 겹침
def calc_v1_loss(students, subjects, master_gene, gene):
    loss = 0
    for student in students.keys():
        time_use = [False for i in range(CPD*5)]
        classes = students[student]
        choices = gene[str(student)]

        assert(len(choices) == len(classes))
        for ind in range(len(choices)):
            choice_now  = choices[ind]
            subject_now = classes[ind] 
            choice_info = get_choice_info(subjects, master_gene, subject_now, choice_now)
            start_times = master_gene[str(subject_now)]["times"][choice_now]

            for c in range(len(start_times)):
                for time in range(start_times[c], start_times[c]+choice_info[c]["len"]):
                    if not time_use[time]:
                        time_use[time] = True
                    else:
                        loss += 1
        
    return loss

# v2: 교사, 강의실 시간 겹침
def calc_v2_loss(data, gene):
    teacher_times = { int(key): [False for i in range(CPD*5)] for key in data["teachers"].keys() }
    room_times = { int(key): [False for i in range(5*CPD)] for key in data["rooms"].keys() }
    loss = 0
    subjects = data["subjects"]
    for subject in subjects.keys():
        my_gene = gene[str(subject)]
        for i in range(len(my_gene["index"])):
            times = my_gene["times"][i]
            sub_data = get_choice_info(subjects, gene, subject, i)
            for t in range(len(times)):
                st_time = times[t]
                sub_len = sub_data[t]["len"]
                for time in range(st_time, st_time+sub_len):
                    if room_times[sub_data[t]["room"]][time]:
                        loss += 1
                    else:
                        room_times[sub_data[t]["room"]][time] = True
                    for teacher in sub_data[t]["teacher"]:
                        if teacher_times[teacher][t]:
                            loss += 1
                        else:
                            teacher_times[teacher][t] = True
    return loss

def crossover(students, master_gene, gene1, gene2):
    CROSS_PROB = 0.3
    mut_prob = MUT_PROB
    
    gene_mat = {}

    child1, child2 = {}, {}

    for student in students.keys():
        child1[student] = []
        child2[student] = []
        for sub in students[student]:
            if sub not in gene_mat:
                div_count = len(master_gene[str(sub)]["index"])
                gene_mat[sub] = [ [[] for j in range(div_count)] for i in range(div_count)]
    
    for student in gene1:
        for i in range(len(gene1[student])):
            sub_now = students[student][i]
            gene_mat[sub_now][gene1[student][i]][gene2[student][i]].append(student)

    for subject in gene_mat.keys():
        # Crossover
        div_count = len(gene_mat[subject])
        for i in range(div_count):
            for j in range(div_count):
                if random.random() < CROSS_PROB:
                    gene_mat[subject][i][j], gene_mat[subject][j][i] = gene_mat[subject][j][i], gene_mat[subject][i][j]
        
        # Mutation
        if random.random() > mut_prob:
            continue
        mut_count = random.randrange(1, int(div_count**2)+1)
        for mut in range(mut_count):
            if div_count == 1:
                i1, i2 = 0, 0
            else:
                ind = random.sample(range(div_count), 2)
                i1, i2 = ind[0], ind[1]
            if len(gene_mat[subject][i1][i2]) == 0 or len(gene_mat[subject][i2][i1]) == 0:
                continue
            t1 = random.randrange(len(gene_mat[subject][i1][i2]))
            t2 = random.randrange(len(gene_mat[subject][i2][i1]))
            gene_mat[subject][i1][i2][t1], gene_mat[subject][i2][i1][t2] = \
                gene_mat[subject][i2][i1][t2], gene_mat[subject][i1][i2][t1]
            break

    # Build child genes
    for subject in gene_mat.keys():
        div_count = len(gene_mat[subject])
        for i in range(div_count):
            for j in range(div_count):
                for std in gene_mat[subject][i][j]:
                    child1[std].append(i)
                    child2[std].append(j)
    return child1, child2


def init_group(data, gene, count=100):
    return [
        create_placement(data["students"], data["subjects"], gene)
        for i in range(count)
    ]

def generation(data, gene, group):
    PROCS = 8

    assert(len(group)%4 == 0)
    count = len(group)
    students = data["students"]
    subjects = data["subjects"]
    # Make children
    for i in range(int(count/2)):
        c1, c2 = crossover(students, gene, group[2*i], group[2*i+1])
        group.append(c1)
        group.append(c2)

    for i in range(int(count/4)):
        create_placement(data["students"], data["subjects"], gene)

    executor = concurrent.futures.ProcessPoolExecutor(PROCS)
    futures = [executor.submit(calc_v1_loss, students, subjects, gene, it) for it in group]
    concurrent.futures.wait(futures)
    # Calculate losses
    group_loss = [
        [group[i], futures[i].result()]
        for i in range(len(group))
    ]
    group_loss = sorted(group_loss, key=itemgetter(1))[:count]

    return [item[0] for item in group_loss], group_loss[0][1]

def run_test(data, gene):
    group = init_group(data, gene, count=POP)
    bests = []
    same_stack = 0
    same_v = 0
    for i in range(GENS):
        st = time.time()
        group, best = generation(data, gene, group)
        en = time.time()
        print('Generation',i,': Best',best)
        print('Elapsed Time:',en-st,'s')
        bests.append(best)
    return bests, group[0]

def evaluate(data, gene, parent_generation=1, gene_id=1):
    rand_id = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(12))

    group = init_group(data, gene, count=POP)
    bests = []
    for i in range(GENS):
        st = time.time()
        group, best = generation(data, gene, group)
        en = time.time()
        # print('Generation',i,': Best',best)
        # print('Elapsed Time:',en-st,'s')
        bests.append(best)
    
    try:
        plt.clf()
        matplotlib.use('Agg')
        plt.plot(range(1,GENS+1), bests)
        plt.xlabel('Generation')
        plt.ylabel('Loss (V1)')
        plt.title('V1 Loss by Generation (Gen '+str(parent_generation)+', No. '+str(gene_id)+')')
        plt.savefig('plot/v1_loss-'+rand_id)
        print('Result saved to plot/v1_loss-'+rand_id)
    except:
        print('Error saving to plot/v1_loss-'+rand_id)

    return [bests[-1], bests]

if __name__ == "__main__":
    with open(config.get("Files","data"), "r", encoding="utf8") as f:
        data = json.load(f)
    with open("test_gene.json", "r", encoding="utf8") as f:
        gene = json.load(f)

    """
    g1 = create_placement(data["students"], data["subjects"], gene)
    g2 = create_placement(data["students"], data["subjects"], gene)
    c1, c2 = crossover(data["students"], gene, g1, g2)

    with open("t1.json", 'w', encoding="utf8") as f:
        json.dump(g1, f, indent=4)

    with open("t2.json", 'w', encoding="utf8") as f:
        json.dump(c1, f, indent=4)
    """

    rand_id = str(random.randrange(10000))
    
    for run in range(5):
        bests, bgene = run_test(data, gene)
        
        try:
            matplotlib.use('Agg')
            plt.plot(range(1,GENS+1), bests)
            plt.xlabel('Generation')
            plt.ylabel('Loss (V1)')
            plt.title('V1 Loss by Generation (w/ Mutation)')
            plt.savefig('plot/v1_loss-'+rand_id+'-'+str(run+1))
            print('Result saved to plot/v1_loss-'+rand_id+'-'+str(run+1))
        except:
            print('Error saving to plot/v1_loss-'+rand_id+'-'+str(run+1))

    """ 
    places = create_placement(
        data["students"],
        data["subjects"],
        gene)
    
    g1 = create_placement(data["students"], data["subjects"], gene)
    g2 = create_placement(data["students"], data["subjects"], gene)
    
    sm = 0
    CNT = 100
    for i in range(CNT):
        st = time.time()
        c1, c2 = crossover(data["students"], gene, g1, g2)
        en = time.time()
        sm += (en-st)
    print("Crossover average time:"+str(sm/CNT*1000)+"ms")
    
    sm = 0
    CNT = 100
    for i in range(CNT):
        st = time.time()
        calc_v1_loss(data["students"], data["subjects"], gene, places)
        en = time.time()
        sm += (en-st)
    print("V1 loss average time: "+str(sm/CNT*1000)+"ms")
    # print(get_choice_info(data["subjects"], gene, 0, 4))
    
    # print(json.dumps(places,indent=4))
    # print(calc_v1_loss(data["students"], places, data["subjects"], gene))
    # print(calc_v2_loss(data, gene))
    """
    