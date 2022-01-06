""" 用户日志记录装饰器
"""
import datetime
import json

from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import request

from .postgresql_helper import PgHelper


def logit():
    """日志记录装饰器函数

    Args:
        event_description (str, optional): 事件描述. Defaults to ''.
    """

    def logging_decorator(func):

        @wraps(func)
        def wrapped_function(*args, **kwargs):
            # 相关信息写入数据库日志表中
            pg_helper = PgHelper()
            current_user = get_jwt_identity()
            param_json = request.json.copy()
            param_json["moduleName"] = func.__module__
            param_json["functionName"] = func.__name__
            event_description = func.__doc__.splitlines()[0]
            pg_helper.execute_sql(
                '''INSERT INTO gy_log(user_guid, user_name, event_description,param_json,event_time) VALUES(%s, %s, %s, %s, %s);''',
                (current_user['userGuid'], current_user['userName'], event_description, json.dumps(param_json), datetime.datetime.now()))

            return func(*args, **kwargs)

        return wrapped_function

    return logging_decorator
