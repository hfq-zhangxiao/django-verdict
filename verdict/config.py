# coding: utf-8
from django.conf import settings


user_model_label = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')
verdict_settings = getattr(settings, 'VERDICT_SETTINGS', {})

PAGE_LIMIT = verdict_settings.get('PAGE_LIMIT', 10)
super_user_filter = verdict_settings.get('SUPER_USER_FILTER', {'is_superuser': 1})
user_model_name_field = verdict_settings.get('USER_MODEL_NAME_FIELD', 'username')
user_model_email_field = verdict_settings.get('USER_MODEL_EMAIL_FIELD', 'email')
user_always_filter = verdict_settings.get('USER_ALWAYS_FILTER', {})
user_always_exclude = verdict_settings.get('USER_ALWAYS_EXCLUDE', {})


default_permission_prefix = '_verdict_'
default_permissions = (
    ('%spermission.create' % default_permission_prefix, '添加权限'),
    ('%spermission.delete' % default_permission_prefix, '删除权限'),
    ('%spermission.update' % default_permission_prefix, '修改权限'),
    ('%spermission.read' % default_permission_prefix, '权限列表'),
    ('%spile.create' % default_permission_prefix, '添加权限集'),
    ('%spile.delete' % default_permission_prefix, '删除权限集'),
    ('%spile.update' % default_permission_prefix, '修改权限集'),
    ('%spile.read' % default_permission_prefix, '权限集列表'),
    ('%spile_permission.update' % default_permission_prefix, '修改权限集权限'),
    ('%suser.read' % default_permission_prefix, '用户列表'),
    ('%sgroup.create' % default_permission_prefix, '群组创建'),
    ('%sgroup.delete' % default_permission_prefix, '群组删除'),
    ('%sgroup.update' % default_permission_prefix, '群组修改'),
    ('%sgroup.read' % default_permission_prefix, '群组列表'),
    ('%sgroup_user.update' % default_permission_prefix, '修改群组成员'),
    ('%sgroup_permission.update' % default_permission_prefix, '修改群组权限'),
)

default_pile_name = '权限管理'


action_enum = {
    'GET': 'read',
    'HEAD': 'read',
    'POST': 'create',
    'PUT': 'update',
    'PATCH': 'update',
    'DELETE': 'delete',
    'OPTIONS': 'read',
}

