Запуск:

```bash
docker-compose up -d --build
```

Чтобы выполнить скрипт:
```bash
docker exec script python -m script.main

Запуск тестов:
docker exec script python -m pytest tests/

Параметры для скрипта:
1) --students (путь к файлу студентов, по умолчанию ./data/students.json)
2) --rooms (путь к файлу комнат, по умолчанию ./data/rooms.json)
3) --format (выходной формат: xml или json, по умолчанию json)

Результаты запросов сохраняются в контейнере script в папке ./data/, например, так можно посмотреть результат первого запроса:
docker exec script cat data/result_0.json

Пояснения по индексам (находятся в ./config/init_schema.sql):
1) Индекс на student.room, т.к. по этому внешнему ключу происходит группировка во всех четырех запросах
2) Составной индекс на students.room и student.birthday, т.к. используем агрегатные функции по birthday (avg во втором запросе, min и max в третьем) после join по room.id = student.room
3) Ещё один составной индекс на student.room и student.sex, для ускорения count(distinct s.sex) > 1 после join по room.id = student.room

Тип для всех трех индексов - B-Tree, т.к. первый индекс на внешний ключ (тип поля - целое число, высокая кардинальность); второй - на внешний ключ и timestamp (поля с высокой кардинальностью, используются в order by, строки с одинаковым student.room будут находится рядом на диске); третий - на внешний ключ и varchar длины 1 (только внешний ключ имеет высокую кардинальность, но student.sex может принимать только два значения, GIN и GiST будут излишни, а BRIN и Hash в принципе не подойдут. Также student.sex используются в having) 
