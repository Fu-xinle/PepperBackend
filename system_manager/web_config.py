""" 前端网页模块,包括读取侧边栏菜单;
"""
import traceback

from flask import (jsonify, request)
from flask_jwt_extended import jwt_required

from toolbox.postgresql_helper import PgHelper

from .blue_print import system_manager_api


@system_manager_api.route('/web_config/sidebar_menu', methods=('POST',))
@jwt_required()
def sidebar_menu():
    """系统的侧边栏菜单
    获取系统的侧边栏菜单，如果存在navnar_menu_guid，
    则为对应navnarMenu菜单下的sidebarMenu
    ---
    tags:
      - system_manager_api/web_config
    parameters:
      - in: string
        name: navnar_menu_guid
        type: string
        required: false
        description: 导航栏菜单的GUID标识
    responses:
      200:
        description: 侧边栏菜单，数组类型
        schema:
          properties:
            path:
              type: string
              description: 菜单的路由路径
            title:
              type: string
              description: 菜单名称
            icon:
              type: string
              description: 菜单图标
            class:
              type: string
              description: 样式类名称
            badge:
              type: string
              description: 显示的提示信息
            badgeClass:
              type: string
              description: 标记的样式类名称
            isExternalLink:
              type: boolean
              description: 是否打开新页面显示
            submenu:
              type: list
              description: 菜单的子菜单，数组类型
            navbar_guid:
              type: string
              description: 导航栏的菜单
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
        if not request.json.get('navnar_menu_guid', None):
            records = pg_helper.query_datatable('''select id,guid,path,title,icon,class,badge,badge_class as badgeClass,
                         is_external_link as isExternalLink,parent_guid,array[]::integer[] as submenu
                                                   from gy_sidebar_menu
                                                   order by sort''')
        else:
            records = pg_helper.query_datatable(
                '''select id,guid,path,title,icon,class,badge,badge_class as badgeClass,
                          is_external_link as isExternalLink,parent_guid,array[]::integer[] as submenu
                                                   from gy_sidebar_menu
                                                   order by sort
                                                   where navbar_guid=%s''', (request.json.get('navnar_menu_guid', None),))

        records_dic = {x['guid']: dict(x.items()) for x in records}
        for x in records:
            if x["parent_guid"]:
                records_dic[x["parent_guid"]]["submenu"].append(dict(x.items()))

        return jsonify({"sidebarMenu": [records_dic[key] for key in records_dic if not records_dic[key]["parent_guid"]]}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500
