"""登录注册模块;包括用户登录;用户注册;手机验证码、微信、支付宝、QQ登录(待开发);
"""
import traceback
import hashlib

from flask import (jsonify, request)
from flask_jwt_extended import create_access_token

from toolbox.postgresql_helper import PgHelper

from .blue_print import system_manage_api


@system_manage_api.route('/login_registration/login', methods=('POST',))
def login():
    """用户登录
    根据用户名和密码验证用户是否存在、密码是否正确；
    验证通过后，获取用户的Token、权限和角色信息
    ---
    tags:
      - system_manage_api/login_registration
    parameters:
      - in: string
        name: userName
        type: string
        required: true
        description: 用户名
      - in: string
        name: password
        type: string
        required: true
        description: 密码
    responses:
      200:
        description: 用户基本信息、Token、权限信息
        schema:
          properties:
            userMessageShow:
              type: boolean
              description: 查询用户不存在信息是否显示
            userMessage:
              type: string
              description: 查询用户不存在信息
            passMessageShow:
              type: boolean
              description: 查询用户密码错误信息是否显示
            passMessage:
              type: string
              description: 查询用户密码错误信息
            token:
              type: string
              description: 用户登录创建的Token值
            userInfo:
              type: object
              description: 用户的基本信息、权限信息等的
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
        record_count = pg_helper.query_single_value("select count(id) from gy_user where user_name=%s", (request.json.get('userName', None),))

        #用户不存在情况
        if record_count == 0:
            return jsonify({
                "userMessageShow": True,
                "userMessage": "用户名不存在",
                "passMessageShow": False,
                "passMessage": "",
                "token": None,
                "userInfo": {}
            }), 200

        # 用户存在查询用户密码
        record_count = pg_helper.query_single_value(
            "select count(id) from gy_user where user_name=%s and password=%s",
            (request.json.get('userName', None), hashlib.md5(request.json.get('password', None).encode(encoding='UTF-8')).hexdigest()))

        # 用户和密码不一致，密码错误
        if record_count == 0:
            return jsonify({
                "userMessageShow": False,
                "userMessage": "",
                "passMessageShow": True,
                "passMessage": "密码错误",
                "token": None,
                "userInfo": {}
            }), 200

        #用户密码正确情况
        #获取用户基本信息
        general_info = pg_helper.query_datatable(
            '''select guid as "userGuid",user_name as "userName",
            real_name as "realName",to_char(birthday,'YYYY-MM-DD') as birthday,academic_degree as "academicDegree",
            gender,email,graduated_school as "graduatedSchool",phone_number as "phoneNumber",
            address,work_place as "workPlace",
            case when photo is null then 'assets/images/avator/default-user.png'
            else 'data:image/png;base64,'||encode(photo::bytea, 'base64') end as photo
            from gy_user where user_name=%s and password=%s''',
            (request.json.get('userName', None), hashlib.md5(request.json.get('password', None).encode(encoding='UTF-8')).hexdigest()))
        user_info = dict(general_info[0])

        #获取用户的权限信息
        return jsonify({
            "userMessageShow": False,
            "userMessage": "",
            "passMessageShow": False,
            "passMessage": "",
            "token": create_access_token(identity={
                'userName': user_info['userName'],
                'userGuid': user_info['userGuid']
            }),
            "userInfo": user_info,
            "permissions": None,
            "role": None
        }), 200
    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manage_api.route('/login_registration/phone_verif', methods=('POST',))
def phone_verif():
    """给手机发送手机验证码
    根据手机号码，给手机发送手机验证码
    ---
    tags:
      - system_manage_api/login_registration
    parameters:
      - in: string
        name: phone
        type: string
        required: true
        description: 手机号
    responses:
      200:
        description: 手机号码的手机验证码
        schema:
          properties:
            phoneVerifCode:
              type: string
              description: 发送的手机验证码
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
        #pg_helper = PgHelper()

        return jsonify({"phoneVerifCode": False}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500
