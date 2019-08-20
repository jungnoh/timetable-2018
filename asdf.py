std_count = 12
choice_count = 3
stds_per_sub = int(std_count/choice_count)
overflow_cnt = std_count - stds_per_sub * choice_count
cs = []
for i in range(overflow_cnt):
    cs.extend([ i for q in range(stds_per_sub+1)])
for i in range(overflow_cnt, choice_count):
    cs.extend([ i for q in range(stds_per_sub)])
print(cs)