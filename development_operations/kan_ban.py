"""团队化开发看板模块,包括读取所有看板;添加看板;编辑看板信息;删除看板;
"""
import traceback
import datetime

from flask import (jsonify, request)
from flask_jwt_extended import (jwt_required, get_jwt_identity)

from toolbox.postgresql_helper import PgHelper
from toolbox.user_log import logit

from .blue_print import development_operations_api


@development_operations_api.route('/kan_ban/all_kan_ban', methods=('get',))
@jwt_required()
def all_kan_ban():
    """所有的算法模型信息
    获取系统的所有算法模型项信息，仅名称和描述
    不包括模型设计
    ---
    tags:
      - system_manage_api/geoprocessing_model
    responses:
      200:
        description: 服务运行成功返回的对象
        schema:
          properties:
            geoprocessingModelData:
              type: array
              description: 地理处理模型数组
              items:
                type: object
                properties:
                  guid:
                    type: string
                    description: 算法模型的唯一标识符
                  name:
                    type: string
                    description: 算法模型名称
                  description:
                    type: string
                    description: 描述
                  createUser:
                    type: string
                    description: 算法模型创建者
                  createTime:
                    type: string
                    description: 算法模型创建时间
                  isLeaf:
                    type: boolean
                    description: 是否是叶节点，即是算法模型还是算法模型类别
                  treeName:
                    type: string
                    description: 算法模型在树结构中的名称，使用~连接树层次名称
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
                                                from gy_geoprocessing_model where parent_guid = '99fb71e8-a794-47c2-a9c6-dc0a6e36248f'
                                                union all
                                                select
                                                origin.guid, origin.name, origin.description,origin.create_user as "createUser",to_char(origin.create_time,'YYYY-MM-DD HH24:MI:SS') as "createTime",origin.is_leaf as "isLeaf",
                                                cte."treeName" || '~' || origin.name,origin.parent_guid as "parentGuid"
                                                from cte,gy_geoprocessing_model origin 
                                                where origin.parent_guid = cte.guid
                                                )
                                                select  guid, name, description,"createUser","createTime","isLeaf","treeName","parentGuid"
                                                from cte;''')

        return jsonify({"geoprocessingModelData": [dict(x.items()) for x in records]}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@development_operations_api.route('/kan_ban/add_kan_ban', methods=('post',))
@jwt_required()
@logit()
def add_kan_ban():
    """添加算法模型项信息
    用户新建算法模型，将新建的算法模型信息保存到到数据库
    ---
    tags:
      - system_manage_api/geoprocessing_model
    parameters:
      - name: newGeoprocessingModelInfo
        type: object
        in: body
        required: true
        description: 新建的算法模型信息
        schema:
          properties:
            guid:
              type: string
              description: 算法模型的唯一标识符
            name:
              type: string
              description: 算法模型名称
            description:
              type: string
              description: 描述
            createUser:
              type: string
              description: 算法模型创建者
            createTime:
              type: string
              description: 算法模型创建时间
            isLeaf:
              type: boolean
              description: 是否是叶节点，即是算法模型还是算法模型类别
            treeName:
              type: string
              description: 算法模型在树结构中的名称，使用~连接树层次名称
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

        request_param = request.json.get('newGeoprocessingModelInfo', None)
        pg_helper.execute_sql(
            '''INSERT INTO gy_geoprocessing_model(guid, name, description,create_user,create_time,parent_guid,is_leaf)
               VALUES(%s, %s, %s, %s, %s, %s, %s);''',
            (request_param.get('guid', None), request_param.get('name', None), request_param.get('description', None), current_user['userName'],
             current_time, request_param.get('parentGuid', None), request_param.get('isLeaf', None)))

        return jsonify({'createUser': current_user['userName'], 'createTime': current_time.strftime("%Y-%m-%d %H:%M:%S")}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@development_operations_api.route('/kan_ban/edit_kan_ban', methods=('post',))
@jwt_required()
@logit()
def edit_kan_ban():
    """编辑更新算法模型项信息
    用户修改算法模型信息，将修改后的算法模型信息保存到到数据库
    ---
    tags:
      - system_manage_api/geoprocessing_model
    parameters:
      - name: editGeoprocessingModelInfo
        type: object
        in: body
        required: true
        description: 新建的算法模型信息
        schema:
          properties:
            guid:
              type: string
              description: 算法模型的唯一标识符
            name:
              type: string
              description: 算法模型名称
            description:
              type: string
              description: 描述
            createUser:
              type: string
              description: 算法模型创建者
            createTime:
              type: string
              description: 算法模型创建时间
            isLeaf:
              type: boolean
              description: 是否是叶节点，即是算法模型还是算法模型类别
            treeName:
              type: string
              description: 算法模型在树结构中的名称，使用~连接树层次名称
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

        request_param = request.json.get('editGeoprocessingModelInfo', None)
        pg_helper.execute_sql(
            '''update gy_geoprocessing_model set name=%s,description=%s,create_user=%s,create_time=%s,parent_guid=%s where guid=%s''',
            (request_param.get('name', None), request_param.get(
                'description', None), current_user['userName'], current_time, request_param.get('parentGuid', None), request_param.get('guid', None)))

        return jsonify({'createUser': current_user['userName'], 'createTime': current_time.strftime("%Y-%m-%d %H:%M:%S")}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@development_operations_api.route('/kan_ban/delete_kan_ban', methods=('post',))
@jwt_required()
@logit()
def delete_kan_ban():
    """删除算法模型项信息
    用户删除算法模型项信息，将信息保存到数据库
    ---
    tags:
      - system_manage_api/geoprocessing_model
    parameters:
      - in: body
        name: guid
        type: string
        required: true
        description: 算法模型信息的guid
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
        pg_helper.execute_sql('''delete from gy_geoprocessing_model where guid=%s''', (request.json.get('guid', None),))

        return jsonify({}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500
