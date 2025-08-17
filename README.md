Запуск:
docker-compose up -d --build

Чтобы выполнить скрипт:
docker exec script python -m script.main

Параметры для скрипта:
1) --students (путь к файлу студентов, по умолчанию ./data/students.json)
2) --rooms (путь к файлу комнат, по умолчанию ./data/rooms.json)
3) --format (выходной формат: xml или json, по умолчанию json)

Результаты запросов сохраняются в контейнере script в папке ./data/, например:
docker exec script cat data/result_0.json
Так можно посмотреть результат первого запроса.