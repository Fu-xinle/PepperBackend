"""团队化开发词汇表模块,包括读取所有词汇对照项;添加词汇对照项;编辑词汇对照项;删除词汇对照项;
"""
import traceback
import datetime

from flask import (jsonify, request)
from flask_jwt_extended import (jwt_required, get_jwt_identity)

from toolbox.postgresql_helper import PgHelper
from toolbox.user_log import logit

from .blue_print import development_operations_api


@development_operations_api.route('/word_chinese_english/all_word_chinese_englishs', methods=('get',))
@jwt_required()
def all_word_chinese_englishs():
    """所有的词汇项信息
    获取系统的所有词汇项信息，树形结构信息
    ---
    tags:
      - development_operations_api/word_chinese_english
    responses:
      200:
        description: 服务运行成功返回的对象
        schema:
          properties:
            wordChineseEnglishData:
              type: array
              description: 词汇项数组
              items:
                type: object
                properties:
                  guid:
                    type: string
                    description: 词汇项的唯一标识符
                  chineseName:
                    type: string
                    description: 词汇项中文名称
                  englishName:
                    type: string
                    description: 词汇项英文名称
                  createUser:
                    type: string
                    description: 词汇项创建者
                  createTime:
                    type: string
                    description: 词汇项创建时间
                  isLeaf:
                    type: boolean
                    description: 是否是叶节点，即是词汇项还是词汇项目录
                  treeChineseName:
                    type: string
                    description: 词汇项在树结构中的名称，使用~连接树层次名称
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
                                                select guid, chinese_name as "chineseName", english_name as "englishName",create_user as "createUser",to_char(create_time,'YYYY-MM-DD HH24:MI:SS') as "createTime",is_leaf as "isLeaf",
                                                chinese_name::text as "treeChineseName",parent_guid as "parentGuid" from gy_word_chinese_english where parent_guid = '4dba9686-8412-4a14-8ddf-a7c48c8e446d'
                                                union all
                                                select
                                                origin.guid, origin.chinese_name as "chineseName", origin.english_name as "englishName",origin.create_user as "createUser",
                                                to_char(origin.create_time,'YYYY-MM-DD HH24:MI:SS') as "createTime",origin.is_leaf as "isLeaf",
                                                cte."treeChineseName" || '~' || origin.chinese_name,origin.parent_guid as "parentGuid"
                                                from cte,gy_word_chinese_english origin 
                                                where origin.parent_guid = cte.guid
                                                )
                                                select  guid, "chineseName", "englishName","createUser","createTime","isLeaf","treeChineseName","parentGuid"
                                                from cte;''')

        return jsonify({"wordChineseEnglishData": [dict(x.items()) for x in records]}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@development_operations_api.route('/word_chinese_english/add_word_chinese_english', methods=('post',))
@jwt_required()
@logit()
def add_word_chinese_english():
    """添加词汇项信息
    用户新建词汇项，将新建的词汇项信息保存到到数据库
    ---
    tags:
      - development_operations_api/word_chinese_english
    parameters:
      - name: newWordChineseEnglishInfo
        type: object
        in: body
        required: true
        description: 新建的词汇项信息
        schema:
          properties:
            guid:
              type: string
              description: 词汇项的唯一标识符
            chineseName:
              type: string
              description: 词汇项中文名称
            englishName:
              type: string
              description: 词汇项英文名称
            createUser:
              type: string
              description: 词汇项创建者
            createTime:
              type: string
              description: 词汇项创建时间
            isLeaf:
              type: boolean
              description: 是否是叶节点，即是词汇项还是词汇项目录
            treeChineseName:
              type: string
              description:词汇项在树结构中的名称，使用~连接树层次名称
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

        request_param = request.json.get('newWordChineseEnglishInfo', None)
        pg_helper.execute_sql(
            '''INSERT INTO gy_word_chinese_english(guid, chinese_name, english_name,create_user,create_time,parent_guid,is_leaf)
               VALUES(%s, %s, %s, %s, %s, %s, %s);''',
            (request_param.get('guid', None), request_param.get('chineseName', None), request_param.get('englishName', None),
             current_user['userName'], current_time, request_param.get('parentGuid', None), request_param.get('isLeaf', None)))

        return jsonify({'createUser': current_user['userName'], 'createTime': current_time.strftime("%Y-%m-%d %H:%M:%S")}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@development_operations_api.route('/word_chinese_english/edit_word_chinese_english', methods=('post',))
@jwt_required()
@logit()
def edit_word_chinese_english():
    """编辑更新词汇项信息
    用户修改词汇项信息，将修改后的词汇项信息保存到到数据库
    ---
    tags:
      - development_operations_api/word_chinese_english
    parameters:
      - name: editWordChineseEnglishInfo
        type: object
        in: body
        required: true
        description: 编辑的词汇项信息
        schema:
          properties:
            guid:
              type: string
              description: 词汇项的唯一标识符
            chineseName:
              type: string
              description: 词汇项中文名称
            englishName:
              type: string
              description: 词汇项英文名称
            createUser:
              type: string
              description: 词汇项创建者
            createTime:
              type: string
              description: 词汇项创建时间
            isLeaf:
              type: boolean
              description: 是否是叶节点，即是词汇项还是词汇项目录
            treeChineseName:
              type: string
              description:词汇项在树结构中的名称，使用~连接树层次名称
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

        request_param = request.json.get('editWordChineseEnglishInfo', None)
        pg_helper.execute_sql(
            '''update gy_word_chinese_english set chinese_name=%s,english_name=%s,create_user=%s,create_time=%s,parent_guid=%s where guid=%s''',
            (request_param.get('chineseName', None), request_param.get(
                'englishName', None), current_user['userName'], current_time, request_param.get('parentGuid', None), request_param.get('guid', None)))

        return jsonify({'createUser': current_user['userName'], 'createTime': current_time.strftime("%Y-%m-%d %H:%M:%S")}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500


@development_operations_api.route('/word_chinese_english/delete_word_chinese_english', methods=('post',))
@jwt_required()
@logit()
def delete_word_chinese_english():
    """删除词汇项信息
    用户删除词汇项信息，保存到数据库
    ---
    tags:
      - development_operations_api/word_chinese_english
    parameters:
      - in: body
        name: guid
        type: string
        required: true
        description: 词汇项的guid
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
        pg_helper.execute_sql('''delete from gy_word_chinese_english where guid=%s''', (request.json.get('guid', None),))

        return jsonify({}), 200

    except Exception as exception:
        return jsonify({"errMessage": repr(exception), "traceMessage": traceback.format_exc()}), 500
