"""流程管理模块,包括读取所有流程;添加流程;编辑流程;删除流程;
   读取流程图;流程图设计保存流程图;
"""
import traceback
import datetime

from flask import (jsonify, request)
from flask_jwt_extended import (jwt_required, get_jwt_identity)

from toolbox.postgresql_helper import PgHelper
from toolbox.user_log import logit

from .blue_print import system_manage_api


@system_manage_api.route('/flow_manage/all_flows', methods=('get',))
@jwt_required()
def all_flows():
    """所有的流程项信息
    获取系统的所有流程信息，不包括流程图信息，
    仅用于添加、编辑流程名称和描述、删除流程信息
    ---
    tags:
      - system_manage_api/flow_manage
    responses:
      200:
        description: 流程信息，数组类型
        schema:
          properties:
            id:
              type: integer
              description: 序号
            guid:
              type: string
              description: 流程的唯一标识符
            name:
              type: string
              description: 流程名称
            description:
              type: string
              description: 描述
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
        records = pg_helper.query_datatable('''select row_number() over(order by id) AS id, guid,name,description from gy_flow
                                               order by id''')

        return jsonify({"flowData": [dict(x.items()) for x in records]}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manage_api.route('/flow_manage/edit_flow', methods=('post',))
@jwt_required()
@logit()
def edit_flow():
    """编辑更新流程项信息
    用户修改流程信息，将修改后的流程信息保存到到数据库
    ---
    tags:
      - system_manage_api/flow_manage
    parameters:
      - in: dict
        name: editFlowInfo
        type: dict
        required: true
        description: 修改后的流程信息
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
        request_param = request.json.get('editFlowInfo', None)
        pg_helper.execute_sql('''update gy_flow set name=%s,description=%s where guid=%s''',
                              (request_param.get('name', None), request_param.get('description', None), request_param.get('guid', None)))

        return jsonify({}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manage_api.route('/flow_manage/delete_flow', methods=('post',))
@jwt_required()
@logit()
def delete_flow():
    """删除流程项信息
    用户删除流程项信息，将信息保存到数据库
    ---
    tags:
      - system_manage_api/flow_manage
    parameters:
      - in: string
        name: guid
        type: string
        required: true
        description: 流程信息的guid
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
        # 删除的信息：流程信息、流程节点信息、工作流关联的本流程设置为NULL
        pg_helper.execute_sql('''delete from gy_flow where guid=%s;delete from gy_flow_node where flow_guid=%s;''',
                              (request.json.get('guid', None), request.json.get('guid', None)))

        return jsonify({}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manage_api.route('/flow_manage/new_and_save_flow', methods=('post',))
@jwt_required()
@logit()
def new_and_save_flow():
    """新建流程以及流程另存为操作，包含保存流程图
    保存流程信息、流程图信息以及流程节点信息
    ---
    tags:
      - system_manage_api/flow_manage
    parameters:
      - in: obeject
        name: flowInfo
        type: obeject
        required: true
        description: 流程信息
      - in: string
        name: diagramJson
        type: string
        required: true
        description: 流程模型流程图的json字符串
      - in: obeject
        name: nodes
        type: obeject
        required: true
        description: 流程模型各个节点信息数组
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

        # 插入流程信息、流程图信息
        current_user = get_jwt_identity()
        flow_info = request.json.get('flowInfo', None)
        sql_string = "INSERT INTO gy_flow(guid, name, description,flow_json,create_user,create_time) VALUES(%s, %s, %s, %s, %s, %s);"
        sql_tuple = sql_tuple + (flow_info.get('guid', None), flow_info.get('name', None), flow_info.get(
            'description', None), request.json.get('diagramJson', None), current_user['userName'], datetime.datetime.now())

        #插入节点的语句，如果节点存在仅仅更新相应的信息
        for x in request.json.get('nodes', None):
            sql_string = sql_string + 'insert into gy_flow_node(guid,node_name,next_node_guid,flow_guid) values(%s,%s,%s,%s);'
            sql_tuple = sql_tuple + (x['guid'], x['nodeName'], x['nextNodeGuid'], flow_info.get('guid', None))

        #数据库操作
        pg_helper = PgHelper()
        pg_helper.execute_sql(sql_string, sql_tuple)

        return jsonify({}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manage_api.route('/flow_manage/flow_diagram', methods=('post',))
@jwt_required()
def flow_diagram():
    """获取流程模型的流程图
    根据自定义模型的guid标识，获取流程模型的流程图
    ---
    tags:
      - system_manage_api/flow_manage
    parameters:
      - in: string
        name: guid
        type: string
        required: true
        description: 流程模型信息的guid
    responses:
      200:
        description: 流程模型的流程图信息，字符串形式
        schema:
          properties:
            diagramJson:
              type: string
              description: 流程模型的流程图信息，字符串形式
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
        diagram_json = pg_helper.query_single_value('select flow_json from gy_flow where guid=%s', (request.json.get('guid', None),))

        return jsonify({"diagramJson": diagram_json}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manage_api.route('/flow_manage/save_flow_diagram', methods=('post',))
@jwt_required()
@logit()
def save_flow_diagram():
    """保存流程模型的流程图以及节点信息
    根据流程模型的guid标识，保存流程模型的流程图以及节点信息
    ---
    tags:
      - system_manage_api/flow_manage
    parameters:
      - in: string
        name: guid
        type: string
        required: true
        description: 流程模型的guid
      - in: string
        name: diagramJson
        type: string
        required: true
        description: 流程模型流程图的json字符串
      - in: obeject
        name: nodes
        type: obeject
        required: true
        description: 流程模型各个节点信息数组
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

        #更新流程图、删除旧的流程图节点
        sql_string = "update gy_flow set flow_json=%s where guid=%s;delete from gy_flow_node where flow_guid=%s;"
        sql_tuple = sql_tuple + (request.json.get('diagramJson', None), request.json.get('guid', None), request.json.get('guid', None))

        #插入节点的语句，如果节点存在仅仅更新相应的信息
        for x in request.json.get('nodes', None):
            sql_string = sql_string + 'insert into gy_flow_node(guid,node_name,next_node_guid,flow_guid) values(%s,%s,%s,%s);'
            sql_tuple = sql_tuple + (x['guid'], x['nodeName'], x['nextNodeGuid'], request.json.get('guid', None))

        #数据库操作
        pg_helper = PgHelper()
        pg_helper.execute_sql(sql_string, sql_tuple)

        return jsonify({}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500
