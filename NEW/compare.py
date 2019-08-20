import numpy as np
import matplotlib.pyplot as plt
import json

def heatmap():
    with open('data/out/out.json', 'r') as f:
        js = json.load(f)
        data = js['students']
        data_cls = js['classes']
    dataset = {}

    for student in data:
        for cl in data[student]:
            if cl not in dataset.keys():
                dataset[cl] = []
            dataset[cl].append(student)
    
    keys = dataset.keys()
    print(keys)
    D = [ set(dataset[cl]) for cl in dataset ]
    conf = [
        [
            len(D[i] & D[j]) / len(D[i])
            for j in range(len(D))
        ]
        for i in range(len(D))
    ]
    plt.figure(figsize=(17, 17))
    plt.title('Heatmap of class confidence: P(Y|X)')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.imshow(conf, cmap='summer', interpolation='nearest', aspect='auto')
    plt.xticks(np.arange(0, len(keys)+1, 1.0))
    plt.yticks(np.arange(0, len(keys)+1, 1.0))
    plt.savefig('data/out/heatmap.png', dpi=100)

    dd = []
    for i in range(len(D)):
        for j in range(len(D)):
            if i == j: continue
            else: dd.append([conf[i][j], i, j])
    
    dd=sorted(dd)
    dd.reverse()
    with open('data/out/conf.txt', 'w') as f:
        for line in dd:
            f.write('%.4f: %s -> %s\r\n' % (line[0], data_cls[str(line[1]+1)]['name'], data_cls[str(line[2]+1)]['name']))

if __name__ == '__main__':
    heatmap()          
