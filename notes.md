# 시간표 파싱 순서
1. students2.csv 파싱
- 파일 위치: parse/parse.py

> open("students2.csv", 'r', encoding='utf16').readlines()

- students2.csv 각 라인의 내용이 'ID, 수업명'
- 수업에 대한 dict 생성 후 (없으면), 학생수++
- 제외할 수업들 알아서 제외 (블랙리스트, 인원수<7 등)
- 제외할 학생들 제외 (1학년?)
- data2.json에 결과 JSON 출력.

2. classes.csv 파싱
- 관련된 코드가 없다???
-  결과물은 input.json 참고. 

3. data2.json 메타데이터 첨가
- 학생수 맞는지 체크
- 반, 선생들에 대해 int 매핑
- 각 정보를 rooms.json, teachers.json, out.json 출력.