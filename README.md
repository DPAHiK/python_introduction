Запуск:
docker-compose up -d --build

Чтобы выполнить скрипт:
docker exec script python -m script.main

Параметры для скрипта:
1) --students (путь к файлу студентов)
2) --rooms (путь к файлу комнат)
3) --format (выходной формат: xml или json)

Результаты запросов сохраняются в контейнере в папке ./data/, например:
docker exec script cat data/result_0.json
Так можно посмотреть результат первого запроса.