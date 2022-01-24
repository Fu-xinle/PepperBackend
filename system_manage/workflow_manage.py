"""业务工作流管理模块,包括读取所有业务工作流;添加业务工作流;编辑业务工作流信息;删除业务工作流等;
"""
import traceback
import datetime

from flask import (jsonify, request)
from flask_jwt_extended import (jwt_required, get_jwt_identity)

from toolbox.postgresql_helper import PgHelper
from toolbox.user_log import logit

from .blue_print import system_manage_api


@system_manage_api.route('/workflow_manage/all_workflows', methods=('get',))
@jwt_required()
def all_workflows():
    """所有的业务工作流信息
    获取系统的所有业务工作流信息，名称、描述、关联的流程、关联的表单
    ---
    tags:
      - system_manage_api/workflow_manage
    responses:
      200:
        description: 服务运行成功返回的对象
        schema:
          properties:
            workflowData:
              type: array
              description: 业务工作流数组
              items:
                type: object
                properties:
                  guid:
                    type: string
                    description:业务工作流的唯一标识符
                  name:
                    type: string
                    description: 业务工作流名称
                  flowGuid:
                    type: string
                    description: 关联的业务工作流的GUID
                  flowName:
                    type: string
                    description: 关联的业务工作流的名称
                  formGuid:
                    type: string
                    description: 关联的表单的GUID
                  formName:
                    type: string
                    description: 关联的表单的名称
                  description:
                    type: string
                    description: 描述
                  createUser:
                    type: string
                    description: 业务工作流创建者
                  createTime:
                    type: string
                    description: 业务工作流创建时间
                  isLeaf:
                    type: boolean
                    description: 是否是叶节点，即是业务工作流还是业务工作流类别
                  treeName:
                    type: string
                    description: 业务工作流在树结构中的名称，使用~连接树层次名称
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
                                                select A.guid, A.name, A.description,A.create_user as "createUser",to_char(A.create_time,'YYYY-MM-DD HH24:MI:SS') as "createTime",A.is_leaf as "isLeaf",
                                                  A.name::text as "treeName",A.parent_guid as "parentGuid",A.flow_guid as "flowGuid",A.form_guid as "formGuid",B.name as "flowName",C.name as "formName"
                                                from gy_workflow A left join gy_flow B on A.flow_guid=B.guid 
                                                                left join gy_form C on A.form_guid=C.guid where A.parent_guid = '03bb1ba4-0aeb-46d7-a99c-f03bcc6ea0d5' 
                                                union all
                                                select origin.guid, origin.name, origin.description,origin.create_user as "createUser",to_char(origin.create_time,'YYYY-MM-DD HH24:MI:SS') as "createTime",
                                                  origin.is_leaf as "isLeaf",cte."treeName" || '~' || origin.name as "treeName",origin.parent_guid as "parentGuid",
                                                  origin.flow_guid as "flowGuid",origin.form_guid as "formGuid",B.name as "flowName",C.name as "formName"
                                                from cte,gy_workflow origin left join gy_flow B on origin.flow_guid=B.guid 
                                                                          left join gy_form C on origin.form_guid=C.guid  where origin.parent_guid = cte.guid
                                                )
                                                select guid, name, description,"createUser","createTime","isLeaf","treeName","parentGuid","flowGuid","flowName","formGuid","formName"
                                                from cte;''')

        return jsonify({"workflowData": [dict(x.items()) for x in records]}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manage_api.route('/workflow_manage/add_workflow', methods=('post',))
@jwt_required()
@logit()
def add_workflow():
    """添加业务工作流信息
    用户新建业务工作流，将新建的业务工作流信息保存到到数据库
    ---
    tags:
      - system_manage_api/workflow_manage
    parameters:
      - name: newWorkflowInfo
        type: object
        in: body
        required: true
        description: 新建的业务工作流信息
        schema:
          properties:
            guid:
              type: string
              description: 业务工作流的唯一标识符
            name:
              type: string
              description: 业务工作流名称
            flowGuid:
                  type: string
                  description: 关联的业务工作流的GUID
            flowName:
              type: string
              description: 关联的业务工作流的名称
            formGuid:
              type: string
              description: 关联的表单的GUID
            formName:
              type: string
              description: 关联的表单的名称
            description:
              type: string
              description: 描述
            createUser:
              type: string
              description: 业务工作流创建者
            createTime:
              type: string
              description: 业务工作流创建时间
            isLeaf:
              type: boolean
              description: 是否是叶节点，即是业务工作流还是业务工作流类别
            treeName:
              type: string
              description: 业务工作流在树结构中的名称，使用~连接树层次名称
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

        request_param = request.json.get('newWorkflowInfo', None)
        pg_helper.execute_sql(
            '''INSERT INTO gy_workflow(guid, name, description,create_user,create_time,parent_guid,flow_guid,form_guid,is_leaf)
               VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s);''', (request_param.get('guid', None), request_param.get(
                'name', None), request_param.get('description', None), current_user['userName'], current_time, request_param.get(
                    'parentGuid', None), request_param.get('flowGuid', None), request_param.get('formGuid', None), request_param.get('isLeaf', None)))

        return jsonify({'createUser': current_user['userName'], 'createTime': current_time.strftime("%Y-%m-%d %H:%M:%S")}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manage_api.route('/workflow_manage/edit_workflow', methods=('post',))
@jwt_required()
@logit()
def edit_workflow():
    """编辑更新业务工作流信息
    用户修改业务工作流信息，将修改后的业务工作流信息保存到到数据库
    ---
    tags:
      - system_manage_api/workflow_manage
    parameters:
      - name: editWorkflowInfo
        type: object
        in: body
        required: true
        description: 编辑的业务工作流信息
        schema:
          properties:
            guid:
              type: string
              description: 业务工作流的唯一标识符
            name:
              type: string
              description: 业务工作流名称
            flowGuid:
                  type: string
                  description: 关联的业务工作流的GUID
            flowName:
              type: string
              description: 关联的业务工作流的名称
            formGuid:
              type: string
              description: 关联的表单的GUID
            formName:
              type: string
              description: 关联的表单的名称
            description:
              type: string
              description: 描述
            createUser:
              type: string
              description: 业务工作流创建者
            createTime:
              type: string
              description: 业务工作流创建时间
            isLeaf:
              type: boolean
              description: 是否是叶节点，即是业务工作流还是业务工作流类别
            treeName:
              type: string
              description: 业务工作流在树结构中的名称，使用~连接树层次名称
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

        request_param = request.json.get('editWorkflowInfo', None)
        pg_helper.execute_sql(
            '''update gy_workflow set name=%s,description=%s,create_user=%s,create_time=%s,parent_guid=%s,flow_guid=%s,form_guid=%s where guid=%s''',
            (request_param.get('name', None), request_param.get(
                'description', None), current_user['userName'], current_time, request_param.get(
                    'parentGuid', None), request_param.get('flowGuid', None), request_param.get('formGuid', None), request_param.get('guid', None)))

        return jsonify({'createUser': current_user['userName'], 'createTime': current_time.strftime("%Y-%m-%d %H:%M:%S")}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manage_api.route('/workflow_manage/delete_workflow', methods=('post',))
@jwt_required()
@logit()
def delete_workflow():
    """删除业务工作流信息
    用户删除业务工作流信息，将信息保存到数据库
    ---
    tags:
      - system_manage_api/workflow_manage
    parameters:
      - in: body
        name: guid
        type: string
        required: true
        description: 业务工作流的guid
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
        pg_helper.execute_sql('''delete from gy_workflow where guid=%s''', (request.json.get('guid', None),))

        return jsonify({}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500
