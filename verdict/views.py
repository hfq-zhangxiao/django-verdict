# coding: utf-8
try:
    from django.urls import reverse
except ImportError as _:
    from django.core.urlresolvers import reverse
from django.db import transaction
from django.views import generic
from django.db.models import Q
from django.http import QueryDict
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404
from django.http.response import JsonResponse

from . import models
from . import exceptions
from .signal import operation_log_signal
from .decorator import required_permission
from .shortcuts import get_user_default_permissions_name, get_user_obj, is_super_user
from .utils import models_to_dict, get_offset_start_end, verify_page, verify_coding, list_result, \
    OperationType
from .config import super_user_filter, user_always_exclude, user_always_filter, user_model_name_field, \
    user_model_email_field, default_permissions, default_permission_prefix, default_pile_name, \
    manage_menu_permissions


default_pile, _ = models.Pile.objects.get_or_create(name=default_pile_name)
default_permission_pile_set = list()
for dp in default_permissions:
    _permission, _ = models.Permission.objects.get_or_create(name=dp[0], defaults={'description': dp[1]})
    default_permission_pile_set.append(models.PermissionPile(permission=_permission, pile=default_pile))
if not models.PermissionPile.objects.filter(pile=default_pile).exists():
    models.PermissionPile.objects.bulk_create(default_permission_pile_set)


class Index(generic.RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        permissions = get_user_default_permissions_name(self.request)
        for permission, view in manage_menu_permissions:
            if permission in permissions:
                return reverse(view)
        raise exceptions.NoPermissionException()


class UserTemplate(generic.TemplateView):
    template_name = 'user.html'
    query_set = get_user_model().objects.filter(**user_always_filter).exclude(
        **user_always_exclude).exclude(**super_user_filter)

    def get_context_data(self, **kwargs):
        page = verify_page(self.request)
        name = verify_coding(self.request.GET.get('name', ''))
        if name:
            name_where = {'%s__contains' % user_model_name_field: name}
            email_where = {'%s__contains' % user_model_email_field: name}
            query_set = self.query_set.filter(Q(**name_where) | Q(**email_where))
        else:
            query_set = self.query_set

        total = query_set.count()
        start, end = get_offset_start_end(page)

        query = query_set.order_by('-pk')
        result = list()
        for obj in query[start:end]:
            user_group = models.GroupUser.objects.filter(user=obj).first()
            result.append({
                'id': obj.pk,
                'name': getattr(obj, user_model_name_field),
                'email': getattr(obj, user_model_email_field),
                'group': dict(name=user_group.group.name, id=user_group.group.id) if user_group else ''
            })
        return list_result(self.request, result, total, page, name=name)

    @required_permission('_verdict_user.read')
    def get(self, request, *args, **kwargs):
        return super(UserTemplate, self).get(request, *args, **kwargs)


class PermissionViewSet(generic.View):
    template_name = 'permission.html'
    query_set = models.Permission.objects.filter(state=1).exclude(
        name__startswith=default_permission_prefix)

    @required_permission('_verdict_permission.read')
    def get(self, request):
        page = verify_page(request)
        name = verify_coding(request.GET.get('name', ''))
        if name:
            query_set = self.query_set.filter(Q(name__contains=name) | Q(description__contains=name))
        else:
            query_set = self.query_set

        total = query_set.count()
        start, end = get_offset_start_end(page)

        query = query_set.order_by('-id')
        result = [models_to_dict(obj) for obj in query[start:end]]
        context = list_result(self.request, result, total, page, name=name)
        return render(request, self.template_name, context)

    @required_permission('_verdict_permission.create')
    def post(self, request):
        required_fields = frozenset(['description', 'name'])
        if not required_fields <= frozenset(request.POST.keys()):
            raise exceptions.MissingFields('missing fields: %s' % list(
                (required_fields - frozenset(request.POST.keys()))))

        name = verify_coding(request.POST['name'])
        description = verify_coding(request.POST['description'])

        if name.startswith(default_permission_prefix):
            return JsonResponse(data=dict(error='invalid name'), status=400)
        if models.Group.objects.filter(state=1, name=name).exists():
            return JsonResponse(data=dict(error='name already exist'), status=400)

        obj = models.Permission.objects.create(name=name, description=description)

        named_args = {
            'user': get_user_obj(request),
            'type': OperationType.CREATE,
            'title': '添加权限[%s]' % name,
            'after': models_to_dict(obj),
        }
        operation_log_signal.send(self.__class__, **named_args)

        return JsonResponse(data=models_to_dict(obj), status=201)


class PermissionUpdateDelete(generic.View):

    @required_permission('_verdict_permission.delete')
    def delete(self, request, pk):
        obj = get_object_or_404(models.Permission, pk=pk)
        if obj.name.startswith(default_permission_prefix):
            return JsonResponse(data=dict(error='can not be deleted'), status=403)
        before = models_to_dict(obj)
        obj.delete()

        named_args = {
            'user': get_user_obj(request),
            'type': OperationType.DELETE,
            'title': '删除权限[%s]' % verify_coding(before['name']),
            'before': before,
        }
        operation_log_signal.send(self.__class__, **named_args)

        return JsonResponse(data=dict(), status=204)

    @required_permission('_verdict_permission.update')
    def patch(self, request, pk):
        obj = get_object_or_404(models.Permission, pk=pk)
        if obj.name.startswith(default_permission_prefix):
            return JsonResponse(data=dict(error='can not be modified'), status=403)
        before = models_to_dict(obj)
        data = QueryDict(request.body)
        if data.get('name'):
            obj.name = verify_coding(data['name'])
        if data.get('description'):
            obj.description = verify_coding(data['description'])
        obj.save()

        named_args = {
            'user': get_user_obj(request),
            'type': OperationType.UPDATE,
            'title': '修改权限[%s]' % before['name'],
            'before': before,
            'after': models_to_dict(obj),
        }
        operation_log_signal.send(self.__class__, **named_args)

        return JsonResponse(data=dict())


class PileViewSet(generic.View):
    template_name = 'pile.html'
    query_set = models.Pile.objects.filter(state=1).exclude(id=default_pile.id)

    @staticmethod
    def _get_pile_child(obj):
        child = dict()
        child['id'] = obj.permission.id
        child['description'] = obj.permission.description
        return child

    @required_permission('_verdict_pile.read')
    def get(self, request):
        page = verify_page(request)
        name = verify_coding(request.GET.get('name', ''))
        if name:
            query_set = self.query_set.filter(name__contains=name)
        else:
            query_set = self.query_set

        total = query_set.count()
        start, end = get_offset_start_end(page)

        query = query_set.order_by('-id')
        result = list()
        for obj in query[start:end]:
            result.append({
                'id': obj.id,
                'name': obj.name,
                'children': [self._get_pile_child(x) for x in models.PermissionPile.objects.filter(
                    state=1, pile=obj
                )]
            })
        context = list_result(self.request, result, total, page, name=name)
        return render(request, self.template_name, context)

    @required_permission('_verdict_pile.create')
    def post(self, request):
        required_fields = frozenset(['name'])
        if not required_fields <= frozenset(request.POST.keys()):
            raise exceptions.MissingFields('missing fields: %s' % list(
                (required_fields - frozenset(request.POST.keys()))))
        name = verify_coding(request.POST['name'])
        if name == verify_coding(default_pile_name):
            return JsonResponse(data=dict(error='invalid name'), status=400)
        if models.Group.objects.filter(state=1, name=name).exists():
            return JsonResponse(data=dict(error='name already exist'), status=400)
        obj = models.Pile.objects.create(name=name)

        named_args = {
            'user': get_user_obj(request),
            'type': OperationType.CREATE,
            'title': '添加权限集[%s]' % name,
            'after': models_to_dict(obj),
        }
        operation_log_signal.send(self.__class__, **named_args)

        return JsonResponse(data=models_to_dict(obj), status=201)


class PileVagrantViewSet(generic.View):

    @required_permission('_verdict_pile.update')
    def get(self, request):
        result = models.Permission.objects.filter(state=1, permissionpile__isnull=True).exclude(
            name__startswith=default_permission_prefix).order_by('name').values('description', 'id')
        return JsonResponse(data=dict(result=list(result)))


class PileUpdateDeleteViewSet(generic.View):

    @required_permission('_verdict_pile.delete')
    def delete(self, request, pk):
        obj = get_object_or_404(models.Pile, pk=pk)
        if obj.id == default_pile.id:
            return JsonResponse(data=dict(error='can not be deleted'), status=400)
        before = models_to_dict(obj)
        obj.delete()

        named_args = {
            'user': get_user_obj(request),
            'type': OperationType.DELETE,
            'title': '删除权限集[%s]' % before['name'],
            'before': before,
        }
        operation_log_signal.send(self.__class__, **named_args)

        return JsonResponse(data=dict(), status=204)

    @required_permission('_verdict_pile.update')
    def patch(self, request, pk):
        obj = get_object_or_404(models.Pile, pk=pk)
        if obj.id == default_pile.id:
            return JsonResponse(data=dict(error='can not be modified'), status=403)
        before = models_to_dict(obj)
        data = QueryDict(request.body)
        if data.get('name'):
            obj.name = verify_coding(data['name'])
        obj.save()

        named_args = {
            'user': get_user_obj(request),
            'type': OperationType.UPDATE,
            'title': '修改权限集[%s]' % before['name'],
            'before': before,
            'after': models_to_dict(obj),
        }
        operation_log_signal.send(self.__class__, **named_args)

        return JsonResponse(data=dict())


class PilePermissionViewSet(generic.View):

    @required_permission('_verdict_pile_permission.update')
    def post(self, request, pk):
        pile = get_object_or_404(models.Pile, pk=pk)
        permissions = request.POST.get('permissions')
        if not permissions:
            return JsonResponse(data=dict(error='missing fields'), status=400)

        has_permissions = map(lambda x: x['permission'],
                              models.PermissionPile.objects.filter(state=1, pile=pile).values('permission'))

        permissions = map(lambda x: int(x.strip()), permissions.strip().split(','))
        pile_permission_set = list()
        for permission_id in permissions:
            permission = models.Permission.objects.filter(state=1, pk=permission_id).first()
            if not permission:
                return JsonResponse(data=dict(error='permission<%s> error' % permission_id), status=400)
            if models.PermissionPile.objects.filter(state=1, permission=permission).exists():
                return JsonResponse(data=dict(
                    error='permission<%s> already exist in a pile' % permission_id), status=400)
            pile_permission_set.append(models.PermissionPile(pile=pile, permission=permission))
        models.PermissionPile.objects.bulk_create(pile_permission_set)

        pile = models_to_dict(pile)
        before = dict(permission=has_permissions)
        before.update(pile)
        after = dict(permission=permissions)
        after.update(pile)

        named_args = {
            'user': get_user_obj(request),
            'type': OperationType.CREATE,
            'title': '添加权限集[%s]权限' % verify_coding(pile['name']),
            'before': before,
            'after': after,
        }
        operation_log_signal.send(self.__class__, **named_args)

        return JsonResponse(data=dict())


class PilePermissionDelete(generic.View):

    @required_permission('_verdict_pile_permission.update')
    def delete(self, request, pile_id, pk):
        pile = get_object_or_404(models.Pile, pk=pile_id)
        permission = get_object_or_404(models.Permission, pk=pk)
        obj = models.PermissionPile.objects.filter(state=1, permission=permission, pile=pile).first()
        if not obj:
            return JsonResponse(data=dict(error='permission not in the pile'), status=400)
        before = models_to_dict(obj)
        obj.delete()

        named_args = {
            'user': get_user_obj(request),
            'type': OperationType.DELETE,
            'title': '删除权限集[%s]权限[%s]' % (verify_coding(pile.name), verify_coding(permission.name)),
            'before': before,
        }
        operation_log_signal.send(self.__class__, **named_args)

        return JsonResponse(data=dict())


class GroupList(generic.View):

    @required_permission('_verdict_group_user.update')
    def get(self, request):
        result = models.Group.objects.filter(state=1).values('id', 'name')
        return JsonResponse(data=dict(result=list(result)))


class GroupViewSet(generic.View):
    template_name = 'group.html'
    query_set = models.Group.objects.filter(state=1)

    @required_permission('_verdict_group.read')
    def get(self, request):
        page = verify_page(request)
        name = verify_coding(request.GET.get('name', ''))
        if name:
            query_set = self.query_set.filter(Q(name__contains=name) | Q(description__contains=name))
        else:
            query_set = self.query_set

        total = query_set.count()
        start, end = get_offset_start_end(page)

        query = query_set.order_by('-id')
        result = list()
        for obj in query[start:end]:
            item = models_to_dict(obj)
            item['member'] = models.GroupUser.objects.filter(state=1, group=obj).count()
            result.append(item)
        context = list_result(self.request, result, total, page, name=name)
        return render(request, self.template_name, context)

    @required_permission('_verdict_group.create')
    def post(self, request):
        required_fields = frozenset(['description', 'name'])
        if not required_fields <= frozenset(request.POST.keys()):
            raise exceptions.MissingFields('missing fields: %s' % list(
                (required_fields - frozenset(request.POST.keys()))))
        name = verify_coding(request.POST['name'])
        description = verify_coding(request.POST['description'])
        if models.Group.objects.filter(state=1, name=name).exists():
            return JsonResponse(data=dict(error='name already exist'), status=400)
        obj = models.Group.objects.create(name=name.strip(), description=description)

        named_args = {
            'user': get_user_obj(request),
            'type': OperationType.CREATE,
            'title': '添加群组[%s]' % name,
            'after': models_to_dict(obj),
        }
        operation_log_signal.send(self.__class__, **named_args)

        return JsonResponse(data=models_to_dict(obj), status=201)


class GroupUpdate(generic.View):

    @required_permission('_verdict_group.delete')
    def delete(self, request, pk):
        obj = get_object_or_404(models.Group, pk=pk)
        before = models_to_dict(obj)
        obj.delete()

        named_args = {
            'user': get_user_obj(request),
            'type': OperationType.DELETE,
            'title': '删除群组[%s]' % verify_coding(before['name']),
            'before': before,
        }
        operation_log_signal.send(self.__class__, **named_args)

        return JsonResponse(data=dict(), status=204)

    @required_permission('_verdict_group.update')
    def patch(self, request, pk):
        obj = get_object_or_404(models.Group, pk=pk)
        before = models_to_dict(obj)
        data = QueryDict(request.body)
        if data.get('name'):
            obj.name = verify_coding(data['name'])
        if data.get('description'):
            obj.description = verify_coding(data['description'])
        obj.save()

        named_args = {
            'user': get_user_obj(request),
            'type': OperationType.UPDATE,
            'title': '修改群组[%s]' % verify_coding(before['name']),
            'before': before,
            'after': models_to_dict(obj),
        }
        operation_log_signal.send(self.__class__, **named_args)

        return JsonResponse(data=dict())


class GroupPermissionViewSet(generic.View):

    @staticmethod
    def _get_pile_child(obj, group_permissions):
        child = dict()
        child['id'] = obj.permission.id
        child['description'] = obj.permission.description
        child['has'] = group_permissions.get(obj.permission.name, False)
        return child

    @required_permission('_verdict_group_permission.update')
    def get(self, request, pk):
        obj = get_object_or_404(models.Group, pk=pk)
        group_permissions = dict(models.Permission.objects.filter(
            state=1,
            grouppermission__state=1,
            grouppermission__group=obj,
        ).values_list('name', 'state'))
        result = list()

        piles = models.Pile.objects.filter(state=1)
        user = get_user_obj(request)
        if not is_super_user(user):
            piles = piles.exclude(name__startswith=default_pile_name)
        for pile in piles:
            item = dict()
            item['name'] = pile.name
            item['children'] = [self._get_pile_child(x, group_permissions)
                                for x in models.PermissionPile.objects.filter(state=1, pile=pile)]
            result.append(item)
        return JsonResponse(data=dict(result=result))

    @required_permission('_verdict_group_permission.update')
    def patch(self, request, pk):
        obj = get_object_or_404(models.Group, pk=pk)
        group = models_to_dict(obj)
        data = QueryDict(request.body)
        if data.get('permissions'):
            permissions = map(lambda x: int(x.strip()), data.get('permissions').strip().split(','))
        else:
            permissions = list()

        has_query = models.Permission.objects.filter(
            state=1, grouppermission__state=1, grouppermission__group=obj)
        group_permission_set = list()
        cur_user = get_user_obj(request)
        if not is_super_user(cur_user):
            has_default_query = has_query.filter(name__startswith=default_permission_prefix)
            permissions.extend(map(lambda x: x['id'], has_default_query.values('id')))
        has_permissions = map(lambda x: x['id'], has_query.values('id'))

        add_permissions = set(permissions).difference(set(has_permissions))
        delete_permission = set(has_permissions).difference(set(permissions))
        for permission_id in add_permissions:
            permission = models.Permission.objects.filter(state=1, pk=permission_id).first()
            if not permission:
                return JsonResponse(data=dict(error='permission<%s> error' % permission_id), status=400)
            group_permission_set.append(models.GroupPermission(group=obj, permission=permission))

        with transaction.atomic():
            models.GroupPermission.objects.bulk_create(group_permission_set)
            models.GroupPermission.objects.filter(
                state=1,
                permission__id__in=list(delete_permission),
            ).delete()

        before = dict(permission=has_permissions)
        before.update(group)
        after = dict(permission=permissions)
        after.update(group)

        named_args = {
            'user': get_user_obj(request),
            'type': OperationType.UPDATE,
            'title': '修改群组[%s]权限' % verify_coding(group['name']),
            'before': before,
            'after': after,
        }
        operation_log_signal.send(self.__class__, **named_args)

        return JsonResponse(data=dict())


class GroupUserList(generic.View):

    @staticmethod
    def _get_user_info(obj):
        user = dict()
        user['name'] = getattr(obj.user, user_model_name_field)
        user['email'] = getattr(obj.user, user_model_email_field)
        return user

    @required_permission('_verdict_group_user.update')
    def get(self, request, pk):
        obj = get_object_or_404(models.Group, pk=pk)
        result = [self._get_user_info(x) for x in
                  models.GroupUser.objects.filter(state=1, group=obj)]
        return JsonResponse(data=dict(result=result))


class GroupUserViewSet(generic.View):

    @required_permission('_verdict_group_user.update')
    def post(self, request, gid, uid):
        group = get_object_or_404(models.Group, pk=gid)
        user = get_object_or_404(get_user_model(), pk=uid)

        if models.GroupUser.objects.filter(state=1, user=user).exists():
            return JsonResponse(data=dict(error='user joined group already'), status=400)
        obj = models.GroupUser.objects.create(group=group, user=user)

        named_args = {
            'user': get_user_obj(request),
            'type': OperationType.CREATE,
            'title': '添加群组[%s]成员[%s]' % (
                verify_coding(group.name), verify_coding(getattr(user, user_model_name_field))),
            'after': models_to_dict(obj),
        }
        operation_log_signal.send(self.__class__, **named_args)

        return JsonResponse(data=dict())

    @required_permission('_verdict_group_user.update')
    def delete(self, request, gid, uid):
        group = get_object_or_404(models.Group, pk=gid)
        user = get_object_or_404(get_user_model(), pk=uid)

        obj = models.GroupUser.objects.filter(state=1, user=user, group=group).first()
        if not obj:
            return JsonResponse(data=dict(error='user are not in the group'), status=400)
        before = models_to_dict(obj)
        obj.delete()

        named_args = {
            'user': get_user_obj(request),
            'type': OperationType.DELETE,
            'title': '删除群组[%s]成员[%s]' % (
                verify_coding(group.name), verify_coding(getattr(user, user_model_name_field))),
            'before': before,
        }
        operation_log_signal.send(self.__class__, **named_args)

        return JsonResponse(data=dict())
