# Parse students.csv, classes.csv from data folder.
import json
import xlsxwriter

students = {}
classes = {}
classname_id = {}

def parse_files():
    classes_file = open("data/in/classes.csv", "r")
    students_file = open("data/in/students.csv", "r")
    blacklist = open("data/in/blacklist", "r").readlines()
    blacklist = [ s.strip() for s in blacklist ]
    
    print(blacklist)

    # students file format: (Student ID), (Class name)
    for line in students_file:
        line = str(line).strip()
        args = line.split(',')
        student, classname = int(args[0]), args[1]
        # print(classname)
        if classname in blacklist:
            continue
        # get class code
        if classname not in classname_id:
            classname_id[classname] = len(classname_id.keys())+1
            classes[classname_id[classname]] = {
                "name": classname,
                "count": 0
            }
        classid = classname_id[classname]
        # add student count
        classes[classname_id[classname]]['count'] += 1
        if student not in students:
            students[student] = []
        students[student].append(classid)

    # sort (just for aesthetics)
    for student in students.keys():
        students[student] = sorted(students[student])

    print('Number of students: %d' % len(students.keys()))
    print('Number of classes: %d' % len(classes.keys()))

    # dump to json file
    with open('data/out/out.json', 'w', encoding='utf-8') as f:
        json.dump({
            'students': students,
            'classes': classes
        }, f, ensure_ascii=False, indent=4)
    
    # dump to xlsx file
    workbook = xlsxwriter.Workbook('data/out/out.xlsx')
    student_worksheet = workbook.add_worksheet()
    student_worksheet.name = 'Student'
    student_worksheet.write(0, 0, 'StudentID')
    student_worksheet.write(0, 1, 'ClassID')
    row = 1
    for student in students.keys():
        for item in students[student]:
            student_worksheet.write(row, 0, student)
            student_worksheet.write(row, 1, item)
            row += 1
    class_worksheet = workbook.add_worksheet()
    class_worksheet.name = 'Classes'
    class_worksheet.write(0, 0, 'ClassID')
    class_worksheet.write(0, 1, 'Name')
    class_worksheet.write(0, 2, 'Count')
    row = 1
    for classid in classes.keys():
        class_worksheet.write(row, 0, classid)
        class_worksheet.write(row, 1, classes[classid]['name'])
        class_worksheet.write(row, 2, classes[classid]['count'])
        row += 1
    workbook.close()

if __name__ == "__main__":
    parse_files()

        