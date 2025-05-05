# -*- encoding: utf-8 -*-
"""
Job Module - khai báo blueprint cho các route liên quan tới jobs
"""

from flask import Blueprint

blueprint = Blueprint(
    'jobs_blueprint',
    __name__,
    url_prefix=''  # hoặc '/jobs' nếu muốn gắn prefix URL
)
