# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Azure App Service sẽ tự chọn cổng qua biến môi trường PORT,
# nên bạn không cần chỉ định bind ở đây.
# Gunicorn mặc định sẽ bind vào 0.0.0.0:8000 nếu không có cổng cụ thể

workers = 1
accesslog = '-'
loglevel = 'debug'
capture_output = True
enable_stdio_inheritance = True
