"""用户管理模块,包括读取所有用户;添加用户;编辑用户信息;删除用户;
   用户与角色配置;
"""
import traceback

from flask import (jsonify, request)
from flask_jwt_extended import jwt_required

from toolbox.postgresql_helper import PgHelper
from toolbox.user_log import logit

from .blue_print import system_manage_api


@system_manage_api.route('/user_manage/all_user', methods=('get',))
@jwt_required()
def all_user():
    """所有的用户信息
    获取系统的所有用户信息，
    用于系统的用户树编辑
    ---
    tags:
      - system_manage_api/user_manage
    responses:
      200:
        description: 角色信息，数组类型
        schema:
          properties:
            id:
              type: integer
              description: 序号
            guid:
              type: string
              description: 用户的唯一标识符
            name:
              type: string
              description: 用户名称
            parent_guid:
              type: string
              description: 父级用户/用户机构的唯一标识
            type:
              type: boolean
              description: 节点是否是用户机构
      500:
        description: 服务运行错误,异常信息
        schema:
          properties:
            errMessage:
              type: string
              description: 异常信息，包括异常信息的类型
            traceMessage:
              type: string
              description: 异常更加详细的信息，包括异常的位置
    """
    try:
        pg_helper = PgHelper()
        records_institution = pg_helper.query_datatable(
            '''select id,guid,name,parent_guid,'false'::boolean as type from gy_user_institution order by id''')
        records_user = pg_helper.query_datatable(
            '''select id,guid,user_name as name,institution_guid as parent_guid,'true'::boolean as type from gy_user order by id''')

        return jsonify({"userData": [dict(x.items()) for x in records_institution] + [dict(x.items()) for x in records_user]}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manage_api.route('/user_manage/add_user', methods=('post',))
@jwt_required()
@logit()
def add_user():
    """添加用户信息
    用户新建用户或者用户机构，
    将用户或用户机构信息添加到数据库
    ---
    tags:
      - system_manage_api/user_manage
    parameters:
      - in: dict
        name: user_info
        type: dict
        required: true
        description: 新建的用户信息
    responses:
      200:
        description: 空，不返回有效数据
      500:
        description: 服务运行错误,异常信息
        schema:
          properties:
            errMessage:
              type: string
              description: 异常信息，包括异常信息的类型
            traceMessage:
              type: string
              description: 异常更加详细的信息，包括异常的位置
    """
    try:
        pg_helper = PgHelper()
        request_param = request.json.get('user_info', None)
        if request_param.get('type', None):
            #新添加的人员，默认密码12345
            pg_helper.execute_sql('''INSERT INTO gy_user(guid,user_name,institution_guid) VALUES(%s, %s, %s);''',
                                  (request_param.get('guid', None), request_param.get('name', None), request_param.get('parent_guid', None)))
        else:
            pg_helper.execute_sql('''INSERT INTO gy_user_institution(guid, name, parent_guid) VALUES(%s, %s, %s);''',
                                  (request_param.get('guid', None), request_param.get('name', None), request_param.get('parent_guid', None)))

        return jsonify({}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manage_api.route('/user_manage/edit_user', methods=('post',))
@jwt_required()
@logit()
def edit_user():
    """编辑更新用户项信息
    用户修改用户信息，将修改后的用户信息保存到到数据库
    ---
    tags:
      - system_manage_api/user_manage
    parameters:
      - in: dict
        name: user_info
        type: dict
        required: true
        description: 修改后的用户信息
    responses:
      200:
        description: 空，不返回有效数据
      500:
        description: 服务运行错误,异常信息
        schema:
          properties:
            errMessage:
              type: string
              description: 异常信息，包括异常信息的类型
            traceMessage:
              type: string
              description: 异常更加详细的信息，包括异常的位置
    """
    try:
        pg_helper = PgHelper()
        request_param = request.json.get('user_info', None)
        if request_param.get('parent_guid', None) is None:
            pg_helper.execute_sql(
                '''update gy_user_institution set name=%s where guid=%s;
                                     update gy_user set user_name=%s where guid=%s''',
                (request_param.get('name', None), request_param.get('guid', None), request_param.get('name', None), request_param.get('guid', None)))
        else:
            pg_helper.execute_sql(
                '''update gy_user_institution set name=%s,parent_guid=%s where guid=%s;
                                     update gy_user set user_name=%s,institution_guid=%s where guid=%s''',
                (request_param.get('name', None), request_param.get('parent_guid', None), request_param.get(
                    'guid', None), request_param.get('name', None), request_param.get('parent_guid', None), request_param.get('guid', None)))

        return jsonify({}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manage_api.route('/user_manage/delete_user', methods=('post',))
@jwt_required()
@logit()
def delete_user():
    """删除用户信息
    用户删除用户信息
    ---
    tags:
      - system_manage_api/user_manage
    parameters:
      - in: string
        name: guid
        type: string
        required: true
        description: 用户信息的guid
    responses:
      200:
        description: 空，不返回有效数据
      500:
        description: 服务运行错误,异常信息
        schema:
          properties:
            errMessage:
              type: string
              description: 异常信息，包括异常信息的类型
            traceMessage:
              type: string
              description: 异常更加详细的信息，包括异常的位置
    """
    try:
        pg_helper = PgHelper()
        pg_helper.execute_sql('''delete from gy_user where guid=%s;delete from gy_user_institution where guid=%s''',
                              (request.json.get('guid', None), request.json.get('guid', None)))

        return jsonify({}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manage_api.route('/user_manage/user_by_role', methods=('post',))
@jwt_required()
def user_by_role():
    """获取用户对应的角色信息
    获取用户对应的角色信息
    ---
    tags:
      - system_manage_api/user_manage
    parameters:
      - in: string
        name: guid
        type: string
        required: true
        description: 用户信息的guid
    responses:
      200:
        description: 空，不返回有效数据
      500:
        description: 服务运行错误,异常信息
        schema:
          properties:
            errMessage:
              type: string
              description: 异常信息，包括异常信息的类型
            traceMessage:
              type: string
              description: 异常更加详细的信息，包括异常的位置
    """
    try:
        pg_helper = PgHelper()
        records = pg_helper.query_datatable('''select role_guid from gy_user_role where user_guid=%s''', (request.json.get('guid', None),))

        return jsonify({"userByRoleArray": records}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manage_api.route('/user_manage/save_user_by_role', methods=('post',))
@jwt_required()
@logit()
def save_user_by_role():
    """保存用户对应的角色信息
    将用户配置的用户对应的角色信息保存到数据库
    ---
    tags:
      - system_manage_api/user_manage
    parameters:
      - in: string
        name: guid
        type: string
        required: true
        description: 用户信息的guid
      - in: array
        name: role_array
        type: array
        required: true
        description: 用户对应的角色信息
    responses:
      200:
        description: 空，不返回有效数据
      500:
        description: 服务运行错误,异常信息
        schema:
          properties:
            errMessage:
              type: string
              description: 异常信息，包括异常信息的类型
            traceMessage:
              type: string
              description: 异常更加详细的信息，包括异常的位置
    """
    try:
        sql_tuple = ()

        sql_string = "delete from gy_user_role where user_guid=%s;"
        sql_tuple = sql_tuple + (request.json.get('guid', None),)

        #构建SQL语句
        for x in request.json.get('role_array', None):
            sql_string = sql_string + '''insert into gy_user_role(user_guid,role_guid) values(%s,%s);'''
            sql_tuple = sql_tuple + (request.json.get('guid', None), x)

        #数据库操作
        pg_helper = PgHelper()
        pg_helper.execute_sql(sql_string, sql_tuple)

        return jsonify({}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500
