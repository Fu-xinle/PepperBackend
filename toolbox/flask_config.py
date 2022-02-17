"""环境配置模块,pylint警告 "R0903: Too few public methods"
   是否使用dictionary or namedtuple代替.(考虑继承特性,仅取消警告)
"""


# pylint: disable=too-few-public-methods
class Config():
    """基本环境配置类
    """
    DEBUG = True
    TESTING = False
    JWT_HEADER_TYPE = 'Pepper'
    JWT_SECRET_KEY = '3d038e0e-7e67-49cc-a318-f886c035c256'
    JWT_ACCESS_TOKEN_EXPIRES = 2592000    #单位为秒，设定为一个月
    SWAGGER = {
        'title': 'API',    #形成API文档的配置
        'uiversion': 3
    }


class ProductionConfig(Config):
    """生产环境配置类
    """
    ...


class DevelopmentConfig(Config):
    """开发环境配置类
    """
    ENV = 'development'


class TestingConfig(Config):
    """测试环境配置类
    """
    TESTING = True
