"""主程序模块
"""
from flasgger import Swagger
from flask import (Flask, redirect, url_for)
from flask_cors import CORS
from flask_jwt_extended import JWTManager
#from flask_socketio import SocketIO, emit
#from werkzeug.security import safe_str_cmp

#蓝图路由导入
from development_operations.blue_print import development_operations_api
from system_manage.blue_print import system_manage_api
from system_manage_authorize.blue_print import system_manage_authorize_api
from technology_research.blue_print import technology_research_api

#FLASK APP主程序
app = Flask(__name__)

#项目的全局配置
app.config.from_object('toolbox.flask_config.DevelopmentConfig')

#蓝图注册
app.register_blueprint(development_operations_api, url_prefix='/development_operations_api')
app.register_blueprint(system_manage_api, url_prefix='/system_manage_api')
app.register_blueprint(system_manage_authorize_api, url_prefix='/system_manage_authorize_api')
app.register_blueprint(technology_research_api, url_prefix='/technology_research_api')

#跨域问题
CORS(app, supports_credentials=True)

#api接口的JWT认证
jwt = JWTManager(app)

#文档生成配置
swagger = Swagger(app)

# WSGI接口在顶层可用，以便wfastcgi获得
wsgi_app = app.wsgi_app


@app.route('/')
def index():
    """ 默认页面，重定向到flasgger的文档页面

    Returns:
        [object]:返回重定向对象
    """
    return redirect(url_for('flasgger.apidocs'))


if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
