""" 日志管理模块,包括分页获取日志记录;
"""
import traceback

from flask import (jsonify, request)
from flask_jwt_extended import jwt_required

from toolbox.postgresql_helper import PgHelper

from .blue_print import system_manage_api


@system_manage_api.route('/log_manage/user_log_server_side_data', methods=('post',))
@jwt_required()
def user_log_server_side_data():
    """用户日志记录，后台分页显示获取
    获取指定分页的用户日志记录
    ---
    tags:
      - system_manage_api/log_manage
    parameters:
      - in: body
        name: totalCount
        type: integer
        required: true
        description: 用户日志记录总数
      - in: body
        name: searchText
        type: string
        required: true
        description: 全局搜索字符串
      - in: body
        name: requestParams
        type: object
        required: true
        description: ag-grid分页请求参数
        schema:
          properties:
            startRow:
                type: integer
                description: 分页的起始行
            endRow:
                type: integer
                description: 分页的结束行
            pivotMode:
                type: boolean
                description: 是否开启pivot模式
            rowGroupCols:
              type: array
              description: 分组的列(未使用)
              items:
                  type: object
            valueCols:
              type: array
              description: 聚合的列(未使用)
              items:
                  type: object
            pivotCols:
              type: array
              description: pivot的列(未使用)
              items:
                  type: object
            groupKeys:
              type: array
              description: 用户正在查看组(未使用)
              items:
                  type: string
            filterModel:
              type: object
              description: 过滤信息对象(未使用)
            sortModel:
              type: array
              description: 排序信息对象
              items:
                  type: object
                  properties:
                    colId:
                      type: string
                      description: 列的唯一标识符
                    sort:
                      type: string
                      description: 升序还是降序
    responses:
      200:
        description: 记录总数与分页请求的数据
        schema:
          properties:
            rowCount:
              type: integer
              description: 用户日志记录总数
            rowData:
              type: array
              description: 分页中当前页的数据
              items:
                type: object
                properties:
                  id:
                    type: integer
                    description: 序号
                  userName:
                    type: string
                    description: 用户名
                  eventDescription:
                    type: string
                    description: 日志中事件描述
                  eventTime:
                    type: string
                    description: 日志中事件时间
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
        total_count = request.json.get('totalCount', None)
        search_text = request.json.get('searchText', None)
        request_params = request.json.get('requestParams', None)

        # 构造查询和排序条件
        limit_count = request_params['endRow'] - request_params['startRow']
        offset_count = request_params['startRow']
        where_cause = ""
        order_cause = ""

        if not (search_text is None or len(search_text) == 0):
            where_cause = " where position('" + search_text + "' in user_name) >0" + " or " + " \
                           position('" + search_text + "' in event_description) >0"

        if request_params['sortModel']:
            order_cause = " order by "
            for sort_item in request_params['sortModel']:
                order_cause = order_cause + " " + sort_item["colId"] + " " + sort_item["sort"] + " "

        # 如果记录总数为空，首先获取记录总数
        if total_count is None:
            total_count = pg_helper.query_single_value(''' select count(id) from gy_log ''' + where_cause)

        # 分页查询
        records = pg_helper.query_datatable('''select row_number() over(''' + order_cause +
                                            ''') AS id, user_name as "userName",event_description as "eventDescription",
            to_char(event_time,'YYYY-MM-DD hh24:mi:ss') as "eventTime" from gy_log''' + where_cause + order_cause + " limit " + str(limit_count) +
                                            " OFFSET " + str(offset_count))

        return jsonify({"rowCount": total_count, "rowData": [dict(x.items()) for x in records]}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500
