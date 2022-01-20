"""表单管理模块,包括读取所有表单;添加表单;编辑表单信息;删除表单;
   读取表单字段;添加字段;删除字段;修改字段;
"""
import traceback
import datetime

from flask import (jsonify, request)
from flask_jwt_extended import (jwt_required, get_jwt_identity)

from toolbox.postgresql_helper import PgHelper
from toolbox.user_log import logit

from .blue_print import system_manage_api


@system_manage_api.route('/form_manage/all_forms', methods=('get',))
@jwt_required()
def all_forms():
    """所有的表单项信息
    获取系统的所有表单项信息，仅名称和描述
    不包括表单设计
    ---
    tags:
      - system_manage_api/form_manage
    responses:
      200:
        description: 表单信息，数组类型
        schema:
          properties:
            geoprocessingModelData:
              type: array
              description: 表单信息数组
              items:
                type: object
                properties:
                  guid:
                    type: string
                    description: 表单的唯一标识符
                  name:
                    type: string
                    description: 表单名称
                  description:
                    type: string
                    description: 描述
                  createUser:
                    type: string
                    description: 表单创建者
                  createTime:
                    type: string
                    description: 表单创建时间
                  isLeaf:
                    type: boolean
                    description: 是否是叶节点，即是表单还是表单类别
                  treeName:
                    type: string
                    description: 表单在树结构中的名称，使用~连接树层次名称
                  parentGuid:
                    type: string
                    description: 父类型的唯一标识
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
        records = pg_helper.query_datatable('''with recursive cte as
                                                (
                                                select guid, name, description,create_user as "createUser",to_char(create_time,'YYYY-MM-DD HH24:MI:SS') as "createTime",is_leaf as "isLeaf",name::text as "treeName",parent_guid as "parentGuid"
                                                from gy_form where parent_guid = 'e6e9ce2a-e960-4349-b5c0-866cb41d3037'
                                                union all
                                                select
                                                origin.guid, origin.name, origin.description,origin.create_user as "createUser",to_char(origin.create_time,'YYYY-MM-DD HH24:MI:SS') as "createTime",origin.is_leaf as "isLeaf",
                                                cte."treeName" || '~' || origin.name,origin.parent_guid as "parentGuid"
                                                from cte,gy_form origin 
                                                where origin.parent_guid = cte.guid
                                                )
                                                select  guid, name, description,"createUser","createTime","isLeaf","treeName","parentGuid"
                                                from cte;''')

        return jsonify({"formData": [dict(x.items()) for x in records]}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manage_api.route('/form_manage/add_form', methods=('post',))
@jwt_required()
@logit()
def add_form():
    """添加表单项信息
    用户新建表单项，将新建的表单项信息保存到到数据库
    ---
    tags:
      - system_manage_api/form_manage
    parameters:
      - in: body
        name: newFormInfo
        type: object
        required: true
        description: 新建的表单项信息
        schema:
          properties:
            guid:
              type: string
              description: 表单的唯一标识符
            name:
              type: string
              description: 表单名称
            description:
              type: string
              description: 描述
            createUser:
              type: string
              description: 表单创建者
            createTime:
              type: string
              description: 表单创建时间
            isLeaf:
              type: boolean
              description: 是否是叶节点，即是表单还是表单类别
            treeName:
              type: string
              description: 表单在树结构中的名称，使用~连接树层次名称
            parentGuid:
              type: string
              description: 父类型的唯一标识
    responses:
      200:
        description: 操作者和操作时间信息
        schema:
          properties:
            createUser:
              type: string
              description: 操作者、用户名称
            createTime:
              type: string
              description: 操作时间
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
        current_user = get_jwt_identity()
        current_time = datetime.datetime.now()

        request_param = request.json.get('newFormInfo', None)
        pg_helper.execute_sql(
            '''INSERT INTO gy_form(guid, name, description,create_user,create_time,parent_guid,is_leaf)
                                 VALUES(%s, %s, %s, %s, %s, %s, %s);''',
            (request_param.get('guid', None), request_param.get('name', None), request_param.get('description', None), current_user['userName'],
             current_time, request_param.get('parentGuid', None), request_param.get('isLeaf', None)))

        return jsonify({'createUser': current_user['userName'], 'createTime': current_time.strftime("%Y-%m-%d %H:%M:%S")}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manage_api.route('/form_manage/edit_form', methods=('post',))
@jwt_required()
@logit()
def edit_form():
    """编辑更新表单项项信息
    用户修改表单项信息，将修改后的表单项信息保存到到数据库
    ---
    tags:
      - system_manage_api/form_manage
    parameters:
      - in: body
        name: editFormInfo
        type: object
        required: true
        description: 修改后的表单项信息
        schema:
          properties:
            guid:
              type: string
              description: 表单的唯一标识符
            name:
              type: string
              description: 表单名称
            description:
              type: string
              description: 描述
            createUser:
              type: string
              description: 表单创建者
            createTime:
              type: string
              description: 表单创建时间
            isLeaf:
              type: boolean
              description: 是否是叶节点，即是表单还是表单类别
            treeName:
              type: string
              description: 表单在树结构中的名称，使用~连接树层次名称
            parentGuid:
              type: string
              description: 父类型的唯一标识
    responses:
      200:
        description: 操作者和操作时间信息
        schema:
          properties:
            createUser:
              type: string
              description: 操作者、用户名称
            createTime:
              type: string
              description: 操作时间
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
        current_user = get_jwt_identity()
        current_time = datetime.datetime.now()

        request_param = request.json.get('editFormInfo', None)
        pg_helper.execute_sql('''update gy_form set name=%s,description=%s,create_user=%s,create_time=%s,parent_guid=%s where guid=%s''',
                              (request_param.get('name', None), request_param.get('description', None), current_user['userName'], current_time,
                               request_param.get('parentGuid', None), request_param.get('guid', None)))

        return jsonify({'createUser': current_user['userName'], 'createTime': current_time.strftime("%Y-%m-%d %H:%M:%S")}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manage_api.route('/form_manage/delete_form', methods=('post',))
@jwt_required()
@logit()
def delete_form():
    """删除表单项项信息
    用户删除表单项项信息，将信息保存到数据库
    ---
    tags:
      - system_manage_api/form_manage
    parameters:
      - in: body
        name: guid
        type: string
        required: true
        description: 表单项信息的guid
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
        pg_helper.execute_sql('''delete from gy_form where guid=%s''', (request.json.get('guid', None),))

        return jsonify({}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manage_api.route('/form_manage/all_fields', methods=('post',))
@jwt_required()
def all_fields():
    """特定表单的字段信息
    获取特定表单的所有字段信息
    ---
    tags:
      - system_manage_api/form_manage
    parameters:
      - in: string
        name: guid
        type: string
        required: true
        description: 获取字段表单的guid
    responses:
      200:
        description: 特定表单的字段信息，数组类型
        schema:
          properties:
            id:
              type: integer
              description: 序号
            guid:
              type: string
              description: 字段的唯一标识符
            name:
              type: string
              description: 字段名称
            type:
              type: string
              description: 字段类型
            group:
              type: string
              description: 字段分组
            controltype:
              type: string
              description: 控件类型
            selectsource:
              type: string
              description: select控件的数据源
            orderid:
              type: integer
              description: 字段排序
            label:
              type: string
              description: 字段标签名称
            edit:
              type: boolean
              description: 是否处于编辑状态
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
        records = pg_helper.query_datatable(
            '''select row_number() over(order by id) AS id,guid,
                                               field_name as name,field_type as type,field_group as group,control_type as controltype,
                                               select_source as selectsource, order_id as orderid,field_label as label, 'false'::boolean as edit
                                               from gy_form_field where form_guid=%s order by id''', (request.json.get('guid', None),))

        return jsonify({"fieldData": [dict(x.items()) for x in records]}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manage_api.route('/form_manage/add_field', methods=('post',))
@jwt_required()
def add_field():
    """添加字段信息
    用户新建添加字段信息
    ---
    tags:
      - system_manage_api/form_manage
    parameters:
      - in: dict
        name: field_info
        type: dict
        required: true
        description: 新建的字段信息
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
        request_param = request.json.get('field_info', None)
        pg_helper.execute_sql(
            '''INSERT INTO gy_form_field(guid,form_guid,field_name,field_type,field_group,control_type,select_source,order_id,field_label)
                                             VALUES(%s, %s, %s,%s, %s, %s,%s, %s,%s);''',
            (request_param.get('guid', None), request_param.get('formGuid', None), request_param.get('name', None), request_param.get(
                'type', None), request_param.get('group', None), request_param.get('controltype', None), request_param.get(
                    'selectsource', None), request_param.get('orderid', None), request_param.get('label', None)))

        return jsonify({}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manage_api.route('/form_manage/edit_field', methods=('post',))
@jwt_required()
def edit_field():
    """编辑更新字段信息
    用户修改字段信息，将修改后的字段项信息保存到到数据库
    ---
    tags:
      - system_manage_api/form_manage
    parameters:
      - in: dict
        name: field_info
        type: dict
        required: true
        description: 修改后的字段信息
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
        request_param = request.json.get('field_info', None)
        pg_helper.execute_sql(
            '''update gy_form_field
                                 set field_name=%s,field_type=%s,field_group=%s,control_type=%s,select_source=%s,order_id=%s,field_label=%s
                                 where guid=%s''', (request_param.get('name', None), request_param.get('type', None), request_param.get(
                'group', None), request_param.get('controltype', None), request_param.get('selectsource', None), request_param.get(
                    'orderid', None), request_param.get('label', None), request_param.get('guid', None)))

        return jsonify({}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manage_api.route('/form_manage/delete_field', methods=('post',))
@jwt_required()
def delete_field():
    """删除字段项信息
    用户删除字段项信息，将信息保存到数据库
    ---
    tags:
      - system_manage_api/form_manage
    parameters:
      - in: string
        name: guid
        type: string
        required: true
        description: 字段项信息的guid
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
        pg_helper.execute_sql('''delete from gy_form_field where guid=%s''', (request.json.get('guid', None),))

        return jsonify({}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500
