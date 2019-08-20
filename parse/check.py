# Check inp with data2 and add metadata in data2 to inp

import json

def main():
    with open("data2.json", "r", encoding="utf8") as f:
        data2 = json.load(f)

    with open("input.json", "r", encoding="utf8") as f:
        inp = json.load(f)

    rooms = []
    teachers = []

    for key in data2["subjects"].keys():
        if inp["subjects"][key]["name"] != data2["subjects"][key]["name"]:
            print(str(key)+" bad!!!!!!")
        else:
            print(str(key)+" ok")

        inp["subjects"][key]["count"] = data2["subjects"][key]["count"]
        inp["subjects"][key]["id"] = data2["subjects"][key]["id"]

        for choice in inp["subjects"][key]["choices"]:
            for item in choice["group"]:
                rooms.append(item["room"])
                for teacher in item["teacher"]:
                    teachers.append(teacher)

    rooms = sorted(set(rooms))
    teachers = sorted(set(teachers))

    for key in data2["subjects"].keys():
        for choice in inp["subjects"][key]["choices"]:
            for item in choice["group"]:
                item["room"] = rooms.index(item["room"])+1
                for i in range(len(item["teacher"])):
                    item["teacher"][i] = teachers.index(item["teacher"][i])+1
    
    rooms = { i+1: rooms[i] for i in range(len(rooms)) }
    teachers = { i+1: teachers[i] for i in range(len(teachers)) }

    final_data = {
        "students": data2["students"],
        "subjects": inp["subjects"],
        "rooms": rooms,
        "teachers": teachers
    }

    with open("out.json", "w", encoding="utf8") as f:
        f.write(json.dumps(inp, ensure_ascii=False, indent=4, sort_keys=False))
    
    with open("rooms.json", "w", encoding="utf8") as f:
        f.write(json.dumps(rooms, ensure_ascii=False, indent=4))
    
    with open("teachers.json", "w", encoding="utf8") as f:
        f.write(json.dumps(teachers, ensure_ascii=False, indent=4))

    with open("merged.json", "w", encoding="utf8") as f:
        f.write(json.dumps(final_data, ensure_ascii=False, indent=4))


if __name__ == "__main__":
    main()
