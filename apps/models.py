from flask import current_app, g
import pymysql
from urllib.parse import urlparse
from apps import db
from apps.jobs.models import Job
from sqlalchemy import func
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

def get_jobs(offset=0, limit=9, experience=None, position=None, job_type=None, location=None):
    query = Job.query

    if experience:
        query = query.filter(func.lower(Job.experience).contains(experience.lower()))
    if position:
        query = query.filter(func.lower(Job.job_title).contains(position.lower()))
    if job_type:
        query = query.filter(func.lower(Job.job_type) == job_type.lower())
    if location:
        query = query.filter(func.lower(Job.location).contains(location.lower()))

    return query.offset(offset).limit(limit).all()

def count_jobs(experience=None, position=None, job_type=None, location=None):
    query = Job.query

    if experience:
        query = query.filter(func.lower(Job.experience).contains(experience.lower()))
    if position:
        query = query.filter(func.lower(Job.job_title).contains(position.lower()))
    if job_type:
        query = query.filter(func.lower(Job.job_type) == job_type.lower())
    if location:
        query = query.filter(func.lower(Job.location).contains(location.lower()))

    return query.count()

