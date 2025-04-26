from flask import current_app, g
import pymysql
from urllib.parse import urlparse

def parse_mysql_uri(uri):
    parsed = urlparse(uri)
    return {
        'host': parsed.hostname,
        'port': parsed.port or 3306,
        'user': parsed.username,
        'password': parsed.password,
        'database': parsed.path.lstrip('/'),
    }

def get_db():
    if 'db' not in g:
        uri = current_app.config['SQLALCHEMY_DATABASE_URI']
        cfg = parse_mysql_uri(uri)
        g.db = pymysql.connect(
            host=cfg['host'],
            user=cfg['user'],
            password=cfg['password'],
            database=cfg['database'],
            port=cfg['port'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db

def get_jobs(offset=0, limit=9):
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM jobs ORDER BY deadline DESC LIMIT %s OFFSET %s", (limit, offset))
        return cursor.fetchall()

def count_jobs():
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as total FROM jobs")
        result = cursor.fetchone()
        return result['total']
