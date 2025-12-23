# url-shortener
A student project for educational purposes: simple URL shortener service built with FastAPI and SQLite.

## Запуск в Docker

- Сборка образа
```
docker build -t url-shortener .
```

- Запуск контейнера
```
docker run -d -p 8000:80 -v url-shortener-data:/app/data --name url-shortener-app url-shortener
```

## Документация API

Доступна по адресу: http://localhost:8000/docs

## Тестирование

- Проверка работоспособности
```
curl http://localhost:8000/health
```

- Создание короткой ссылки
```
curl -X POST "http://localhost:8000/shorten"
-H "Content-Type: application/json"
-d '{"url": "https://example.com"}'
```

- Использование короткой ссылки (необходимо заменить `abc123` на нужный short_id)
```
curl -L "http://localhost:8000/abc123"
```

- Просмотр статистики
```
curl "http://localhost:8000/stats/abc123"
```
