import os
import redis
import psycopg2
from flask import Flask

app = Flask(__name__)

# Подключаемся к Redis
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

# Функция для работы с PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'postgres'),
        database=os.getenv('DB_NAME', 'counter'),
        user=os.getenv('DB_USER', 'admin'),
        password=os.getenv('DB_PASSWORD', 'secret')
    )

# Создаем таблицу при первом запуске
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS visits (
            id SERIAL PRIMARY KEY,
            count INTEGER DEFAULT 0
        )
    ''')
    cur.execute("INSERT INTO visits (count) SELECT 0 WHERE NOT EXISTS (SELECT 1 FROM visits)")
    conn.commit()
    cur.close()
    conn.close()

@app.route('/')
def hello():
    # Пытаемся получить счетчик из Redis
    cached_count = redis_client.get('visit_count')
    
    if cached_count:
        count = int(cached_count)
        # Обновляем БД
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE visits SET count = count + 1 RETURNING count")
        new_count = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        # Обновляем кеш
        redis_client.set('visit_count', new_count)
        count = new_count
    else:
        # Если кеша нет, берем из БД
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE visits SET count = count + 1 RETURNING count")
        count = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        # Сохраняем в кеш
        redis_client.set('visit_count', count)
    
    return f"""
    <html>
        <body style="font-family: Arial; text-align: center; margin-top: 50px;">
            <h1>🐳 Docker Counter App</h1>
            <h2>Вы посетитель номер: <span style="color: red;">{count}</span></h2>
            <p>Счетчик хранится в PostgreSQL, кешируется в Redis</p>
            <hr>
            <small>Запущено на Fedora Linux</small>
        </body>
    </html>
    """

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
