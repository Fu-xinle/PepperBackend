"""postgresql数据库操作模块，使用psycopg2包,
   一直存在建立连接执行数据库操作后立即关闭连接，还是一个用户登录后一直保持一个连接??
"""
import psycopg2
import psycopg2.extras


class PgHelper:
    """ Python操作PostgreSQL数据库的类
    相关详细描述
    类的相关属性描述
    """
    __connection__ = None
    __cursor__ = None

    def __init__(self):
        """ 类的构造函数,创建数据库连接,打开游标进行数据库操作
        参数：
        返回值：
        """
        try:
            self.__connection__ = psycopg2.connect(host="192.168.1.177", port="5432", dbname="pepper", user="postgres", password="Gis123")
            self.__cursor__ = self.__connection__.cursor(cursor_factory=psycopg2.extras.DictCursor)
        except Exception:
            ...
            raise

    def query_datatable(self, sql_string, param_tuple=None):
        """查询函数,查询多条记录
           self.__cursor__.execute("SELECT (%s %% 2) = 0 AS even", (10,))
        参数：
           sql_string：SQL语句（SELECT等）
           param_tuple：参数元组
        返回值：
           列表形式
           [(1, 100, "abc'def"), (2, None, 'dada'), (3, 42, 'bar')]
        """
        try:
            self.__cursor__.execute(sql_string, param_tuple)
            query_result = self.__cursor__.fetchall()
            self.__connection__.commit()
            return query_result
        except Exception:
            self.__connection__.rollback()
            raise

    def query_single_value(self, sql_string, param_tuple=None):
        """查询函数,查询单个数值 SELECT COUNT(*) FROM等
        参数：
           sql_string：SQL语句（SELECT等）
           param_tuple：参数元组
        返回值：
           单个数值
        """
        try:
            self.__cursor__.execute(sql_string, param_tuple)
            query_result = (self.__cursor__.fetchone())[0]
            self.__connection__.commit()
            return query_result
        except Exception:
            self.__connection__.rollback()
            raise

    def execute_sql(self, ddml_sql, param_tuple=None):
        """SQL语句执行函数,多个语句使用分号;分割
              INSERT INTO some_table (an_int, a_date, a_string) VALUES (%s, %s, %s);
              (10, datetime.date(2005, 11, 18), "O'Reilly")
        参数：
           sql_string：SQL语句（Insert、Update、Delete等）
           param_tuple：参数元组
        返回值：
        """
        try:
            self.__cursor__.execute(ddml_sql, param_tuple)
            self.__connection__.commit()
        except Exception:
            self.__connection__.rollback()
            raise

    def execute_func(self, func_name, param_tuple=None):
        """执行PostgreSQL数据库中写的函数或者过程
           __cursor__.callproc('function name', tuple)与
           __cursor__.execute('select * from functionanme(%s)', tuple)相同
        参数：
           func_name：函数名称
           param_tuple：参数元组;通知支持命名参数
        返回值：
           数据库中函数的返回值
        """
        try:
            self.__cursor__.callproc(func_name, param_tuple)
            query_result = self.__cursor__.fetchall()
            self.__connection__.commit()
            return query_result
        except Exception:
            self.__connection__.rollback()
            raise

    def __del__(self):
        """ 类的析构函数,清除数据库连接,清除数据库游标
        """
        if self.__cursor__ is not None:
            self.__cursor__.close()
            self.__cursor__ = None
        if self.__connection__ is not None:
            self.__connection__.close()
            self.__connection__ = None
