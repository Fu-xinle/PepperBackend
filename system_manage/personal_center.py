"""个人中心模块，包括用户电话、学校、地址等用户信息管理;用户头像管理;
"""
import traceback

from flask import (jsonify, request)
from flask_jwt_extended import jwt_required

from toolbox.postgresql_helper import PgHelper
from toolbox.user_log import logit

from .blue_print import system_manage_api


@system_manage_api.route('/personal_center/gender_option', methods=('get',))
@jwt_required()
def gender_option():
    """性别配置信息
    获取性别的Select控件的选项配置信息
    ---
    tags:
      - system_manage_api/personal_center
    responses:
      200:
        description: 性别配置信息，数组类型
        schema:
          properties:
            genderOptions:
              type: array
              description: 性别配置信息数组
              items:
                type: object
                properties:
                   code:
                     type: string
                     description: 标识代码
                   name:
                     type: string
                     description: 名称
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
        records = pg_helper.query_datatable('''select code,name from gy_gender_config order by id''')

        return jsonify({"genderOptions": [dict(x.items()) for x in records]}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manage_api.route('/personal_center/academic_degree_option', methods=('get',))
@jwt_required()
def academic_degree_option():
    """学位学历配置信息
    获取学位学历Select控件的选项配置信息
    ---
    tags:
      - system_manage_api/personal_center
    responses:
      200:
        description: 学位学历配置信息，数组类型
        schema:
          properties:
            academicDegreeOptions:
              type: array
              description: 学位学历配置信息数组
              items:
                type: object
                properties:
                   code:
                     type: string
                     description: 标识代码
                   name:
                     type: string
                     description: 名称
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
        records = pg_helper.query_datatable('''select code,name from gy_academic_degree_config order by id''')

        return jsonify({"academicDegreeOptions": [dict(x.items()) for x in records]}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manage_api.route('/personal_center/user_info_field_save', methods=('post',))
@jwt_required()
@logit()
def user_info_field_save():
    """更新用户信息字段
    用户信息页面中，更新各字段信息
    ---
    tags:
      - system_manage_api/personal_center
    parameters:
      - in: body
        name: userGuid
        type: string
        required: true
        description: 用户的唯一标识
      - in: body
        name: fieldName
        type: string
        required: true
        description: 数据库字段名称
      - in: body
        name: fieldValue
        type: string
        required: true
        description: 更新的字段的值
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
        user_guid = request.json.get('userGuid', None)
        field_name = request.json.get('fieldName', None)
        field_value = request.json.get('fieldValue', None)

        pg_helper.execute_sql('''update gy_user set ''' + field_name + '''=%s where guid=%s''', (field_value, user_guid))

        return jsonify({}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manage_api.route('/personal_center/update_photo', methods=('post',))
@jwt_required()
@logit()
def update_photo():
    """更新用户的头像照片
    用户信息页面中，上传照片裁切上传
    ---
    tags:
      - system_manage_api/personal_center
    parameters:
      - in: body
        name: userGuid
        type: string
        required: true
        description: 用户的唯一标识
      - in: body
        name: photoString
        type: string
        required: true
        description: 照片的string字符串表示
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
        user_guid = request.json.get('userGuid', None)
        photo_string = request.json.get('photoString', None)

        pg_helper.execute_sql('''update gy_user set photo=decode(%s, 'base64') where guid=%s''', (photo_string, user_guid))

        return jsonify({}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500
