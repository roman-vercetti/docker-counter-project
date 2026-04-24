# 🐳 Docker Counter App

![Docker](https://img.shields.io/badge/Docker-20.10+-blue)
![Python](https://img.shields.io/badge/Python-3.11-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Redis](https://img.shields.io/badge/Redis-7-red)
![Nginx](https://img.shields.io/badge/Nginx-1.25-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

Production-ready многоконтейнерное приложение на Docker Compose с Flask, PostgreSQL, Redis и Nginx.

## 📋 Оглавление

- [Архитектура](#-архитектура)
- [Технологии](#-технологии)
- [Быстрый старт](#-быстрый-старт)
- [Команды для управления](#-команды-для-управления)
- [Технические детали](#-технические-детали)
- [Мониторинг и отладка](#-мониторинг-и-отладка)
- [Тестирование](#-тестирование)
- [Устранение проблем](#-устранение-проблем)

## 🖥 Интерфейс

![App Screenshot](screenshot.png)

## 🏗 Архитектура

### Общая архитектура приложения

```mermaid
graph TB
    User[Пользователь <br>Browser] -->|http://localhost:8080| Nginx[Nginx <br>Reverse Proxy :80]
    Nginx -->|proxy_pass| Flask[Flask App <br>Python :5000]
    Flask -->|Read/Write| PostgreSQL[(PostgreSQL 15 <br>Primary Database)]
    Flask -->|Cache Get/Set| Redis[(Redis 7 <br>Cache Layer)]
    
    style User fill:#1976D2,color:#fff,stroke:#0D47A1,stroke-width:2px
    style Nginx fill:#F57C00,color:#fff,stroke:#E65100,stroke-width:2px
    style Flask fill:#388E3C,color:#fff,stroke:#1B5E20,stroke-width:2px
    style PostgreSQL fill:#7B1FA2,color:#fff,stroke:#4A148C,stroke-width:2px
    style Redis fill:#D32F2F,color:#fff,stroke:#B71C1C,stroke-width:2px
```

### Схема сетевой изоляции

```mermaid
graph LR
    subgraph "Host Machine"
        User[Пользователь <br>:8080]
    end
    subgraph "Docker Networks"
        subgraph "frontend-network"
            Nginx[Nginx <br>Reverse Proxy]
        end
        subgraph "backend-network"
            App[Flask App]
            DB[(PostgreSQL)]
            Cache[(Redis)]
        end
    end
    User -->|"Port mapping <br>8080→80"| Nginx
    Nginx -->|"Internal <br>communication"| App
    App -->|"5432"| DB
    App -->|"6379"| Cache
    
    style User fill:#1976D2,color:#fff,stroke:#0D47A1,stroke-width:2px
    style Nginx fill:#F57C00,color:#fff,stroke:#E65100,stroke-width:2px
    style App fill:#388E3C,color:#fff,stroke:#1B5E20,stroke-width:2px
    style DB fill:#7B1FA2,color:#fff,stroke:#4A148C,stroke-width:2px
    style Cache fill:#D32F2F,color:#fff,stroke:#B71C1C,stroke-width:2px
```
### Взаимодействие сервисов (Sequence Diagram)

```mermaid
sequenceDiagram
    participant Browser
    participant Nginx
    participant Flask
    participant Redis
    participant PostgreSQL

    Browser->>Nginx: GET / HTTP/1.1
    Nginx->>Flask: Proxy pass to :5000
    
    Flask->>Redis: GET visit_count
    alt Cache Hit
        Redis->>Flask: cached_value
        Flask->>PostgreSQL: UPDATE count + 1
        PostgreSQL->>Flask: new_count
        Flask->>Redis: SET visit_count = new_count
    else Cache Miss
        Flask->>PostgreSQL: UPDATE count + 1
        PostgreSQL->>Flask: new_count
        Flask->>Redis: SET visit_count = new_count
    end
    
    Flask->>Nginx: HTML with count
    Nginx->>Browser: HTTP 200 OK
```

### Контейнерная архитектура (Docker)

```mermaid
graph TD
    subgraph "Docker Compose Project"
        
        subgraph "Container: nginx"
            NginxConf["/etc/nginx/nginx.conf"]
            NginxPort["Port 80 (exposed)"]
        end
        
        subgraph "Container: app (Flask)"
            AppCode["/app/app.py"]
            PythonEnv[Python 3.11]
            AppPort["Port 5000"]
        end
        
        subgraph "Container: postgres"
            PGData["/var/lib/postgresql/data"]
            PGPort["Port 5432"]
        end
        
        subgraph "Container: redis"
            RedisData["/data"]
            RedisPort["Port 6379"]
        end
        
        subgraph "Volumes"
            VolumePG[postgres_data]
            VolumeRedis[redis_data]
        end
        
        VolumePG -.-> PGData
        VolumeRedis -.-> RedisData
        
        NginxConf -.->|bind mount| NginxPort
        AppCode -.->|build context| PythonEnv
    end
    
    style NginxConf fill:#FF9800,color:#fff,stroke:#E65100,stroke-width:2px
    style AppCode fill:#4CAF50,color:#fff,stroke:#2E7D32,stroke-width:2px
    style PGData fill:#9C27B0,color:#fff,stroke:#6A1B9A,stroke-width:2px
    style RedisData fill:#F44336,color:#fff,stroke:#C62828,stroke-width:2px
```

## ⚙️ Технологии

| Компонент | Технология | Версия | Назначение |
|-----------|------------|--------|------------|
| **Reverse Proxy** | Nginx | Alpine 1.25 | Балансировка, статика |
| **Web Framework** | Flask | 3.0 | API + Web UI |
| **База данных** | PostgreSQL | 15 Alpine | Persistent storage |
| **Кеш** | Redis | 7 Alpine | Кеширование |
| **Язык** | Python | 3.11 Slim | Application logic |

## 🚀 Быстрый старт

### Требования

- Docker 20.10+
- Docker Compose 2.0+
- Git (опционально)

## Установка и запуск

- 1. Клонировать репозиторий
git clone https://github.com/YOUR_USERNAME/docker-counter-project.git
cd docker-counter-project

- 2. Запустить все сервисы
docker compose up -d

- 3. Открыть в браузере
http://localhost:8080

- 4. Проверить статус
docker compose ps

## 📝 Команды для управления

- Запуск всех сервисов (фон)
docker compose up -d

- Остановка всех сервисов
docker compose down

- Перезапуск с пересборкой образов
docker compose up -d --build

- Просмотр логов
docker compose logs -f

- Масштабирование приложения
docker compose up -d --scale app=3

- Полная очистка (с удалением БД)
docker compose down -v

## Использование Makefile

- make help      # Показать все команды
- make up        # Запустить сервисы
- make down      # Остановить сервисы
- make logs      # Показать логи
- make clean     # Очистить всё (с volumes)
- make test      # Запустить нагрузочное тестирование

## 🔧 Технические детали

### Healthchecks
```bash
# PostgreSQL
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U admin -d counter"]
  interval: 10s
  timeout: 5s
  retries: 5

# Flask App  
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/"]
  interval: 30s
  timeout: 3s
  retries: 3
```

### Изоляция сетей

- **frontend-network**: Только Nginx и Flask (публичный доступ)
- **backend-network**: PostgreSQL и Redis (приватные сети)

### Persistent Volumes

```yaml
volumes:
  postgres_data:  # Данные БД сохраняются
  redis_data:     # Кеш Redis переживает рестарты
```

## 📊 Мониторинг и отладка

### Проверка состояния
```bash
# Статус всех контейнеров
docker compose ps

# Healthcheck приложения
docker inspect counter-app | grep -A 5 "Health"

# Логи конкретного сервиса
docker compose logs --tail=50 postgres
```

### Проверка данных
```bash
# Просмотр счетчика в БД
docker exec -it counter-postgres psql -U admin -d counter -c "SELECT * FROM visits;"

# Просмотр кеша в Redis
docker exec -it counter-redis redis-cli get visit_count
```

## 🧪 Тестирование

### Smoke тесты
```bash
# 1. Проверка доступности
curl -I http://localhost:8080 | grep "200 OK"

# 2. Проверка ответа приложения
curl http://localhost:8080 | grep "счетчик"

# 3. Проверка healthcheck
curl http://localhost:8080/health
```

### Тест отказоустойчивости
```bash
# Остановка Redis (graceful degradation)
docker stop counter-redis
curl http://localhost:8080  # Должен работать через БД
docker start counter-redis   # Восстановление кеша
```

## 🐛 Устранение проблем

### Проблема 1: Порт 8080 уже используется
```bash
# Изменить порт в docker-compose.yml
ports:
  - "8081:80"  # вместо 8080:80
```

### Проблема 2: Permission denied на Linux
```bash
sudo usermod -aG docker $USER
newgrp docker
```

Проблема 3: База данных не создается
```yaml
# Полная перезагрузка с очисткой volumes
docker compose down -v
docker compose up -d
```

## 🗺️ Roadmap

-  Базовый функционал (Flask + PostgreSQL)
-  Redis кеширование
-  Nginx reverse proxy
-  Healthchecks и сети
-  Prometheus + Grafana
-  GitHub Actions CI/CD
-  Kubernetes deployment

## 📄 Лицензия

MIT License

## 👤 Автор

**Roman Petukhov**

- GitHub: [Roman](https://github.com/roman-vercetti)
- Проект: [docker-counter-project](https://github.com/roman-vercetti/docker-counter-project)