"""权限管理模块,包括读取所有权限;添加权限;编辑权限;删除权限
"""
import traceback

from flask import (jsonify, request)
from flask_jwt_extended import jwt_required

from toolbox.postgresql_helper import PgHelper
from toolbox.user_log import logit

from .blue_print import system_manager_api


@system_manager_api.route('/authority_manager/all_authorize', methods=('get',))
@jwt_required()
def all_authorize():
    """所有的权限信息
    获取系统的所有权限信息，
    用于系统的权限树编辑
    ---
    tags:
      - system_manager_api/authority_manager
    responses:
      200:
        description: 权限信息，数组类型
        schema:
          properties:
            id:
              type: integer
              description: 序号
            guid:
              type: string
              description: 权限的唯一标识符
            name:
              type: string
              description: 权限名称
            parent_guid:
              type: string
              description: 父级权限的唯一标识
            type:
              type: boolean
              description: 节点是否是权限节点
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
        records = pg_helper.query_datatable('''select id,guid,name,parent_guid,type from gy_authorize order by id''')

        return jsonify({"authorizeData": [dict(x.items()) for x in records]}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manager_api.route('/authority_manager/add_authorize', methods=('post',))
@jwt_required()
@logit()
def add_authorize():
    """添加权限信息
    用户新建权限或者权限类别，将新建的权限或权限类别信息添加到数据库
    ---
    tags:
      - system_manager_api/authority_manager
    parameters:
      - in: dict
        name: authorize_info
        type: dict
        required: true
        description: 新建的权限信息
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
        request_param = request.json.get('authorize_info', None)
        pg_helper.execute_sql('''INSERT INTO gy_authorize(guid, name, parent_guid,type) VALUES(%s, %s, %s, %s);''', (request_param.get(
            'guid', None), request_param.get('name', None), request_param.get('parent_guid', None), request_param.get('type', None)))

        return jsonify({}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manager_api.route('/authority_manager/edit_authorize', methods=('post',))
@jwt_required()
@logit()
def edit_authorize():
    """编辑更新权限项信息
    用户修改权限信息，将修改后的权限信息保存到到数据库
    ---
    tags:
      - system_manager_api/authority_manager
    parameters:
      - in: dict
        name: authorize_info
        type: dict
        required: true
        description: 修改后的权限信息
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
        request_param = request.json.get('authorize_info', None)
        if request_param.get('parent_guid', None) is None:
            pg_helper.execute_sql('''update gy_authorize set name=%s where guid=%s''',
                                  (request_param.get('name', None), request_param.get('guid', None)))
        else:
            pg_helper.execute_sql('''update gy_authorize set name=%s,parent_guid=%s where guid=%s''',
                                  (request_param.get('name', None), request_param.get('parent_guid', None), request_param.get('guid', None)))

        return jsonify({}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manager_api.route('/authority_manager/delete_authorize', methods=('post',))
@jwt_required()
@logit()
def delete_authorize():
    """删除权限信息
    用户删除权限信息
    ---
    tags:
      - system_manager_api/authority_manager
    parameters:
      - in: string
        name: guid
        type: string
        required: true
        description: 权限信息的guid
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
        pg_helper.execute_sql('''delete from gy_authorize where guid=%s''', (request.json.get('guid', None),))

        return jsonify({}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500
