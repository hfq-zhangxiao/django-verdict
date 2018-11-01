from django.db import models

from .config import user_model_label


class BaseModel(models.Model):

    id = models.AutoField(db_column='f_id', primary_key=True)
    create_time = models.DateTimeField(db_column='f_create_time', auto_now_add=True)
    update_time = models.DateTimeField(db_column='f_update_time', auto_now=True)
    state = models.BooleanField(db_column='f_state', default=True)

    class Meta:
        abstract = True


class Permission(BaseModel):

    name = models.CharField(db_column='f_name', max_length=128, unique=True, null=False, blank=False)
    description = models.CharField(db_column='f_description', max_length=64)

    class Meta:
        db_table = 't_verdict_permission'


class Pile(BaseModel):

    name = models.CharField(db_column='f_name', max_length=128, unique=True, null=False, blank=False)

    class Meta:
        db_table = 't_verdict_pile'


class PermissionPile(BaseModel):
    pile = models.ForeignKey(Pile, db_column='f_pile_id', db_index=True)
    permission = models.ForeignKey(Permission, db_column='f_permission_id', db_index=True)

    class Meta:
        db_table = 't_verdict_permission_pile'


class Group(BaseModel):

    name = models.CharField(db_column='f_name', max_length=64, unique=True, null=False,
                            blank=False)
    description = models.CharField(db_column='f_description', max_length=64)

    class Meta:
        db_table = 't_verdict_group'


class GroupPermission(BaseModel):

    group = models.ForeignKey(Group, db_column='f_group_id', db_index=True)
    permission = models.ForeignKey(Permission, db_column='f_permission_id', db_index=True)

    class Meta:
        db_table = 't_verdict_group_permission'
        unique_together = ['group', 'permission', 'state']


class GroupUser(BaseModel):

    group = models.ForeignKey(Group, db_column='f_group_id', db_index=True)
    user = models.ForeignKey(user_model_label, db_column='f_user_id',
                             related_name='user_id', db_index=True)

    class Meta:
        db_table = 't_verdict_group_user'
        unique_together = ['group', 'user', 'state']
