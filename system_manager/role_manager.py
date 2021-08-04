"""角色管理模块,包括读取所有角色;添加角色;编辑角色;删除角色;
   角色与权限配置;
"""
import traceback

from flask import (jsonify, request)
from flask_jwt_extended import jwt_required

from toolbox import (PgHelper, logit)

from .blue_print import system_manager_api


@system_manager_api.route('/role_manager/all_role', methods=('get',))
@jwt_required()
def all_role():
    """所有的角色信息
    获取系统的所有角色信息，
    用于系统的角色树编辑
    ---
    tags:
      - system_manager_api/role_manager
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
              description: 角色的唯一标识符
            name:
              type: string
              description: 角色名称
            parent_guid:
              type: string
              description: 父级角色/角色类别的唯一标识
            type:
              type: boolean
              description: 节点是否是角色节点
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
        records = pg_helper.query_datatable('''select id,guid,name,parent_guid,type from gy_role order by id''')

        return jsonify({"roleData": [dict(x.items()) for x in records]}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manager_api.route('/role_manager/add_role', methods=('post',))
@jwt_required()
@logit()
def add_role():
    """添加角色信息
    用户新建角色或者角色类别，
    将角色或角色类别信息添加到数据库
    ---
    tags:
      - system_manager_api/role_manager
    parameters:
      - in: dict
        name: role_info
        type: dict
        required: true
        description: 新建的角色信息
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
        request_param = request.json.get('role_info', None)
        pg_helper.execute_sql('''INSERT INTO gy_role(guid, name, parent_guid,type) VALUES(%s, %s, %s, %s);''', (request_param.get(
            'guid', None), request_param.get('name', None), request_param.get('parent_guid', None), request_param.get('type', None)))

        return jsonify({}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manager_api.route('/role_manager/edit_role', methods=('post',))
@jwt_required()
@logit()
def edit_role():
    """编辑更新角色项信息
    用户修改角色信息，将修改后的角色信息保存到到数据库
    ---
    tags:
      - system_manager_api/role_manager
    parameters:
      - in: dict
        name: role_info
        type: dict
        required: true
        description: 修改后的角色信息
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
        request_param = request.json.get('role_info', None)
        if request_param.get('parent_guid', None) is None:
            pg_helper.execute_sql('''update gy_role set name=%s where guid=%s''', (request_param.get('name', None), request_param.get('guid', None)))
        else:
            pg_helper.execute_sql('''update gy_role set name=%s,parent_guid=%s where guid=%s''',
                                  (request_param.get('name', None), request_param.get('parent_guid', None), request_param.get('guid', None)))

        return jsonify({}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manager_api.route('/role_manager/delete_role', methods=('post',))
@jwt_required()
@logit()
def delete_role():
    """删除角色信息
    用户删除角色信息
    ---
    tags:
      - system_manager_api/role_manager
    parameters:
      - in: string
        name: guid
        type: string
        required: true
        description: 角色信息的guid
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
        pg_helper.execute_sql('''delete from gy_role where guid=%s''', (request.json.get('guid', None),))

        return jsonify({}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manager_api.route('/role_manager/role_by_authorize', methods=('post',))
@jwt_required()
def role_by_authorize():
    """获取角色对应的权限信息
    获取角色对应的权限信息
    ---
    tags:
      - system_manager_api/role_manager
    parameters:
      - in: string
        name: guid
        type: string
        required: true
        description: 角色信息的guid
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
        records = pg_helper.query_datatable('''select authorize_guid from gy_role_authorize where role_guid=%s''', (request.json.get('guid', None),))

        return jsonify({"roleByAuthorizeArray": records}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manager_api.route('/role_manager/save_role_by_authorize', methods=('post',))
@jwt_required()
@logit()
def save_role_by_authorize():
    """保存角色对应的权限信息
    将用户配置的角色对应的权限信息保存到数据库
    ---
    tags:
      - system_manager_api/role_manager
    parameters:
      - in: string
        name: guid
        type: string
        required: true
        description: 角色信息的guid
      - in: array
        name: authorize_array
        type: array
        required: true
        description: 角色对应的权限信息
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

        sql_string = "delete from gy_role_authorize where role_guid=%s;"
        sql_tuple = sql_tuple + (request.json.get('guid', None),)

        #构建SQL语句
        for x in request.json.get('authorize_array', None):
            sql_string = sql_string + '''insert into gy_role_authorize(role_guid,authorize_guid) values(%s,%s);'''
            sql_tuple = sql_tuple + (request.json.get('guid', None), x)

        #数据库操作
        pg_helper = PgHelper()
        pg_helper.execute_sql(sql_string, sql_tuple)

        return jsonify({}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500
