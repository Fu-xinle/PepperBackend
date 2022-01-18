"""地理处理模型管理模块,包括读取所有地理处理模型;添加地理处理模型;编辑地理处理模型信息;删除地理处理模型;
   读取地理处理模型设计图;地理处理模型设计保存;地理处理模型运行;
"""
import traceback
import types
import datetime

from flask import (jsonify, request)
from flask_jwt_extended import (jwt_required, get_jwt_identity)

from toolbox.postgresql_helper import PgHelper
from toolbox.user_log import logit
from toolbox import geoprocessing_algorithm

from .blue_print import system_manage_api


@system_manage_api.route('/geoprocessing_model/all_geoprocessing_model', methods=('get',))
@jwt_required()
def all_geoprocessing_model():
    """所有的算法模型信息
    获取系统的所有算法模型项信息，仅名称和描述
    不包括模型设计
    ---
    tags:
      - system_manage_api/geoprocessing_model
    responses:
      200:
        description: 算法模型信息，数组类型
        schema:
          properties:
            id:
              type: integer
              description: 序号
            guid:
              type: string
              description: 算法模型的唯一标识符
            name:
              type: string
              description: 算法模型名称
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
        records = pg_helper.query_datatable('''with recursive cte as
                                                (
                                                select guid, name, description,create_user,to_char(create_time,'YYYY-MM-DD HH24:MI:SS') as create_time,is_leaf,name::text as tree_name,parent_guid
                                                from gy_geoprocessing_model where parent_guid = '99fb71e8-a794-47c2-a9c6-dc0a6e36248f'
                                                union all
                                                select
                                                origin.guid, origin.name, origin.description,origin.create_user,to_char(origin.create_time,'YYYY-MM-DD HH24:MI:SS') as create_time,origin.is_leaf,
                                                cte.tree_name || '~' || origin.name,origin.parent_guid
                                                from cte,gy_geoprocessing_model origin 
                                                where origin.parent_guid = cte.guid
                                                )
                                                select  guid, name, description,create_user,create_time,is_leaf,tree_name,parent_guid
                                                from cte;''')

        return jsonify({"geoprocessingModelData": [dict(x.items()) for x in records]}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manage_api.route('/geoprocessing_model/add_geoprocessing_model', methods=('post',))
@jwt_required()
@logit()
def add_geoprocessing_model():
    """添加算法模型项信息
    用户新建算法模型，将新建的算法模型信息保存到到数据库
    ---
    tags:
      - system_manage_api/geoprocessing_model
    parameters:
      - in: dict
        name: newGeoprocessingModelInfo
        type: dict
        required: true
        description: 新建的算法模型信息
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
        current_user = get_jwt_identity()
        current_time = datetime.datetime.now()

        request_param = request.json.get('newGeoprocessingModelInfo', None)
        pg_helper.execute_sql(
            '''INSERT INTO gy_geoprocessing_model(guid, name, description,create_user,create_time,parent_guid,is_leaf)
               VALUES(%s, %s, %s, %s, %s, %s, %s);''',
            (request_param.get('guid', None), request_param.get('name', None), request_param.get('description', None), current_user['userName'],
             current_time, request_param.get('parentGuid', None), request_param.get('isLeaf', None)))

        return jsonify({'create_user': current_user['userName'], 'create_time': current_time.strftime("%Y-%m-%d %H:%M:%S")}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manage_api.route('/geoprocessing_model/edit_geoprocessing_model', methods=('post',))
@jwt_required()
@logit()
def edit_geoprocessing_model():
    """编辑更新算法模型项信息
    用户修改算法模型信息，将修改后的算法模型信息保存到到数据库
    ---
    tags:
      - system_manage_api/geoprocessing_model
    parameters:
      - in: dict
        name: editGeoprocessingModelInfo
        type: dict
        required: true
        description: 修改后的算法模型信息
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
        current_user = get_jwt_identity()
        current_time = datetime.datetime.now()

        request_param = request.json.get('editGeoprocessingModelInfo', None)
        pg_helper.execute_sql(
            '''update gy_geoprocessing_model set name=%s,description=%s,create_user=%s,create_time=%s,parent_guid=%s where guid=%s''',
            (request_param.get('name', None), request_param.get('description', None), current_user['userName'], current_time,
             request_param.get('parent_guid', None), request_param.get('guid', None)))

        return jsonify({'create_user': current_user['userName'], 'create_time': current_time.strftime("%Y-%m-%d %H:%M:%S")}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manage_api.route('/geoprocessing_model/delete_geoprocessing_model', methods=('post',))
@jwt_required()
@logit()
def delete_geoprocessing_model():
    """删除算法模型项信息
    用户删除算法模型项信息，将信息保存到数据库
    ---
    tags:
      - system_manage_api/geoprocessing_model
    parameters:
      - in: string
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


@system_manage_api.route('/geoprocessing_model/geoprocessing_model_stencils', methods=('get',))
@jwt_required()
def geoprocessing_model_stencils():
    """获取自定义算法包的函数模板
    获取自定义的算法包中各个模块名称、函数的参数、返回值等信息
    用于算法模型的流程图调用
    ---
    tags:
      - system_manage_api/geoprocessing_model
    responses:
      200:
        description: 算法包中的模块信息、模块中的函数信息
        schema:
          properties:
            module_annotations:
              type: object
              description: 模块的注释，{ module_name:module_annotations,...}
            function_annotations:
              type: object
              description: 函数注释， { module_name:[{function_annotations},{},{}...],...}
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
        module_annotations = {}
        function_annotations = {}
        pg_helper = PgHelper()
        #获取注册的空间数据

        #循环包下所有的模块，即空间运算的算法
        for module_name, module_object in geoprocessing_algorithm.__dict__.items():
            if not module_name.startswith('__'):
                module_annotations[module_name] = module_object.__annotations__
                function_annotations[module_name] = []
                #内层循环，循环每个包下的所有函数注解
                for function_name, function_object in module_object.__dict__.items():
                    if (not function_name.startswith('__')) and isinstance(function_object, types.FunctionType):
                        function_annotations[module_name].append(function_object.__annotations__)

        #获取已有的地理处理模型
        records = pg_helper.query_datatable('''select guid,name,'MODEL' as category  from gy_geoprocessing_model''')

        return jsonify({"geoprocessingModelData": [dict(x.items()) for x in records]}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manage_api.route('/geoprocessing_model/geoprocessing_model_diagram', methods=('post',))
@jwt_required()
def geoprocessing_model_diagram():
    """获取自定义算法模型的流程图
    根据自定义模型的guid标识，获取自定义算法模型的流程图
    ---
    tags:
      - system_manage_api/geoprocessing_model
    parameters:
      - in: string
        name: guid
        type: string
        required: true
        description: 算法模型信息的guid
    responses:
      200:
        description: 算法模型的流程图信息，字符串形式
        schema:
          properties:
            geoprocessing_model_diagram:
              type: string
              description: 算法模型的流程图信息，字符串形式
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
        diagram_json = pg_helper.query_single_value('select diagram from gy_geoprocessing_model where guid=%s', (request.json.get('guid', None),))

        return jsonify({"geoprocessing_model_diagram": diagram_json}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manage_api.route('/geoprocessing_model/save_geoprocessing_model_diagram', methods=('post',))
@jwt_required()
def save_geoprocessing_model_diagram():
    """保存自定义算法模型的流程图以及节点信息
    根据算法模型的guid标识，保存算法模型的节点数据、流程图信息
    ---
    tags:
      - system_manage_api/geoprocessing_model
    parameters:
      - in: string
        name: guid
        type: string
        required: true
        description: 算法模型的guid
      - in: string
        name: diagramJson
        type: string
        required: true
        description: 算法模型流程图的json字符串
      - in: obeject
        name: nodes
        type: obeject
        required: true
        description: 算法模型各个节点信息数组
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

        #更新流程图、删除旧的算法图节点
        sql_string = '''update gy_geoprocessing_model set diagram=%s where guid=%s;
                      delete from gy_geoprocessing_model_node where geoprocessing_model_guid=%s;'''

        sql_tuple = sql_tuple + (request.json.get('diagram_json', None), request.json.get('guid', None), request.json.get('guid', None))

        #插入节点的语句，如果节点存在仅仅更新相应的信息
        for x in request.json.get('nodes', None)["parameterArray"]:
            sql_string = sql_string + '''insert into gy_geoprocessing_model_node(guid,module_name,function_name,parameter_name,from_module_name,
                                                                       from_function_name,from_name,from_type,function_name_zh_cn,parameter_name_zh_cn,geoprocessing_model_guid)
                                                                values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);'''
            sql_tuple = sql_tuple + (x['guid'], x['moduleName'], x['functionName'], x['name'], x['fromModuleName'], x['fromFunctionName'],
                                     x['fromName'], x['fromType'], x['functionNameZhCn'], x['nameZhCn'], request.json.get('guid', None))

        #数据库操作
        pg_helper = PgHelper()
        pg_helper.execute_sql(sql_string, sql_tuple)

        return jsonify({}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manage_api.route('/geoprocessing_model/geoprocessing_model_parameters', methods=('post',))
@jwt_required()
def geoprocessing_model_parameters():
    """获取算法模型的需要设置的参数
    根据算法模型的guid标识，获取算法模型需要填写的参数
    ---
    tags:
      - system_manage_api/geoprocessing_model
    parameters:
      - in: string
        name: guid
        type: string
        required: true
        description: 流程模型的guid
    responses:
      200:
        description: 算法模型需要填写的参数，参数数组
        schema:
          properties:
            geoprocessing_model_parameters:
              type: object
              description: 参数数组，[{guid,module_name,function_name,function_name_zh_cn,parameter_name,parameter_name_zh_cn,default_value},{},...]
            geoprocessing_model_diagram:
              type: string
              description: 算法模型的流程图
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
        #查询算法模型参数信息
        pg_helper = PgHelper()
        records = pg_helper.query_datatable(
            '''select guid,module_name,function_name,function_name_zh_cn,parameter_name,parameter_name_zh_cn,null as default_value
                                                   from gy_geoprocessing_model_node
                                                   where geoprocessing_model_guid=%s and from_name is null''', (request.json.get('guid', None),))
        records_list = [dict(x.items()) for x in records]

        #查询算法模型的流程图
        diagram_json = pg_helper.query_single_value('select diagram from gy_geoprocessing_model where guid=%s', (request.json.get('guid', None),))

        return jsonify({"geoprocessing_model_parameters": records_list, "geoprocessing_model_diagram": diagram_json}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@system_manage_api.route('/geoprocessing_model/exec_geoprocessing_model', methods=('post',))
@jwt_required()
def exec_geoprocessing_model():
    """算法模型试运行测试
    根据算法模型的guid标识，算法模型的输入参数，运行算法模型
    ---
    tags:
      - system_manage_api/geoprocessing_model
    parameters:
      - in: string
        name: guid
        type: string
        required: true
        description: 流程模型的guid
      - in: array
        name: param
        type: array
        required: true
        description: 算法模型的初始化参数
    responses:
      200:
        description: 算法模型运行的结果，结果数组
        schema:
          properties:
            geoprocessing_model_result:
              type: object
              description: 结果数组，[{"function_name":"","value":""},{},...]
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
        # exe_functinons_param = {}
        # exe_functinons_already = {}
        # exe_functinons_result = {}

        # param_dic = {x["guid"]: x["default_value"] for x in list(request.json.get('param', []))}

        # #根据算法模型的guid，从数据库中获取所有的函数信息
        # #包括模块、名函数名、参数名称等
        # pg_helper = PgHelper()
        # records = pg_helper.query_datatable(
        #     '''select module_name,function_name,parameter_name,guid,
        #         from_module_name,from_function_name,from_name
        #           from gy_geoprocessing_model_node
        #                                            where geoprocessing_model_guid=%s''', (request.json.get('guid', None),))
        # for x in records:
        #     if not (x["module_name"], x["function_name"]) in exe_functinons_param:
        #         exe_functinons_param[(x["module_name"], x["function_name"])] = {}
        #         exe_functinons_already[(x["module_name"], x["function_name"])] = False

        #     if x["guid"] in param_dic:
        #         exe_functinons_param[(x["module_name"], x["function_name"])][x["parameter_name"]] = param_dic[x["guid"]]
        #     else:
        #         exe_functinons_param[(x["module_name"], x["function_name"])][x["parameter_name"]] = None
        #         exe_functinons_result[(x["from_module_name"], x["from_function_name"], x["from_name"])] = (x["module_name"], x["function_name"],
        #                                                                                                    x["parameter_name"])

        # flag_loop = True
        # latest_result = {}
        # while flag_loop:
        #     flag_loop = False
        #     #循环每一个函数
        #     for key_f in exe_functinons_param:

        #         #函数已经运行过
        #         if exe_functinons_already[key_f]:
        #             continue

        #         #如果一个函数的所有参数值都不是None，在运行所有的函数
        #         func_exeable = True
        #         for key_p in exe_functinons_param[key_f]:
        #             if exe_functinons_param[key_f][key_p] is None:
        #                 func_exeable = False
        #                 flag_loop = True
        #                 break

        #         #运行函数
        #         if func_exeable:
        #             latest_result = {}
        #             exe_functinons_already[key_f] = True
        #             temp_result = geoprocessing_algorithm.__dict__[key_f[0]].__dict__[key_f[1]](**exe_functinons_param[key_f])
        #             #将结果赋给相应的参数
        #             for key_re in temp_result:
        #                 if key_f + (key_re,) in exe_functinons_result:
        #                     exe_functinons_param[exe_functinons_result[key_f +
        #                                                                (key_re,)][:-1]][exe_functinons_result[key_f +
        #                                                                                                       (key_re,)][-1]] = temp_result[key_re]
        #             latest_result[key_f] = temp_result

        # #将最新一次的运行结果进行解析，返回前段
        # ret_string = ""
        # for key_f in latest_result:
        #     for x in geoprocessing_algorithm.__dict__[key_f[0]].__dict__[key_f[1]].__annotations__["return"]:
        #         if x["name_en"] in latest_result[key_f]:
        #             ret_string = ret_string + x["name_zh_cn"] + ":" + str(latest_result[key_f][x["name_en"]]) + "\n"

        # return jsonify({"geoprocessing_model_result": ret_string}), 200
        return jsonify({}), 200
    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500
