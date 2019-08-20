import json
import sys
import io
import jsonpickle


file = open("data/in/students2.csv", 'r', encoding='utf16').readlines()
blacklist = [txt[0:-1] for txt in open("blacklist.txt", 'r', encoding='utf8').readlines()]

ppl = {}
sub = {}
sub_names = []
rm_classes = []
rm_students = []

for i in range(len(file)):
    ls = file[i].split(',')
    ls[0] = int(ls[0])
    ls[1] = ls[1].strip()
    if ls[0] not in ppl.keys():
        ppl[ls[0]] = []
    if ls[1] in sub_names:
        index = sub_names.index(ls[1])
        ppl[ls[0]].append(index)
        sub[index]["students"] += 1
    elif ls[1] == blacklist[0]:
        rm_students.append(ls[0])
    else:
        index = len(sub_names)
        sub_names.append(ls[1])
        sub[index] = {
            "students": 1,
            "name": ls[1]
        }
        ppl[ls[0]].append(index)

for cl in sub.keys():
    if sub[cl]['students'] < 7:
        rm_classes.append(cl)
    elif sub[cl]['name'] in blacklist:
        rm_classes.append(cl)

for key in rm_students:
    for i in ppl[key]:
        sub[i]["students"] -= 1
    ppl.pop(key)

for key in rm_classes:
    sub.pop(key)

for person in ppl:
    for i in rm_classes:
        if i in ppl[person]:
            ppl[person].remove(i)

fout = open("data2.json", mode="w", encoding='utf8')

# print(str.format("{0} students", len(ppl.keys())))
# print(str.format("{0} subjects", len(sub.keys())))

fout.write("{\n")
fout.write("    \"students\":\n")
fout.write("    {\n")

ind = 0
for i in sorted(ppl.keys()):
    ppl[i].sort()
    fout.write(str.format("        \"{0}\": {1}", i, str(ppl[i])))
    if ind != len(ppl.keys())-1:
        fout.write(',')
    fout.write("\n")
    ind += 1

fout.write("    },\n")
fout.write("    \"subjects\":\n")
fout.write("    {\n")

ind = 0
for i in sorted(sub.keys()):
    fout.write("        \""+str(i)+"\": {\n")
    fout.write('            "id": "'+str(i)+'",\n')
    fout.write('            "count": '+str(sub[i]["students"])+",\n")
    fout.write('            "name": "'+str(sub[i]["name"])+'"\n')
    fout.write("        }")
    if ind != len(sub.keys())-1:
        fout.write(',')
    fout.write("\n")
    ind += 1

fout.write("    }\n")
fout.write("}")
