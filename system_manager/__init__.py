"""系统管理模块,包括登录、注册等授权管理;权限管理;角色管理;用户管理;日志管理;个人信息、个人中心;
   流程管理;表单管理;地理处理模型管理;详情见下表：
---------------------------------------------------------------------------------------------------------------
     __init__.py        |       编写者       |                                  功能概述
---------------------------------------------------------------------------------------------------------------
     blue_print.py      |       编写者       |                                  功能概述
---------------------------------------------------------------------------------------------------------------
  authority_manager.py  |       编写者       |                                  功能概述
---------------------------------------------------------------------------------------------------------------
    role_manager.py     |       编写者       |                                  功能概述
---------------------------------------------------------------------------------------------------------------
    user_manager.py     |       编写者       |                                  功能概述
---------------------------------------------------------------------------------------------------------------
    form_manager.py     |       编写者       |                                  功能概述
---------------------------------------------------------------------------------------------------------------
    flow_manager.py     |       编写者       |                                  功能概述
---------------------------------------------------------------------------------------------------------------
 geoprocessing_model.py |       编写者       |                                  功能概述
---------------------------------------------------------------------------------------------------------------
    log_manager.py      |       编写者       |                                  功能概述
---------------------------------------------------------------------------------------------------------------
  personal_center.py    |       编写者       |                                  功能概述
---------------------------------------------------------------------------------------------------------------
  login_registration.py |       编写者       |                                  功能概述
---------------------------------------------------------------------------------------------------------------
     web_config.py      |       编写者       |                                  功能概述
---------------------------------------------------------------------------------------------------------------
"""

from . import (authority_manager, flow_manager, form_manager, geoprocessing_model, log_manager, login_registration, personal_center, role_manager,
               user_manager, web_config)
