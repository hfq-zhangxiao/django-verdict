import os
from django.conf.urls import url
from django.views.static import serve
from django.views.decorators.csrf import csrf_exempt

from . import views


urlpatterns = [
    url(r'^user/$', views.UserTemplate.as_view(), name='verdict_user_view'),

    url(r'^permission/$', csrf_exempt(views.PermissionViewSet.as_view()), name='verdict_permission_view'),
    url(r'^permission/(?P<pk>\d+)/$', csrf_exempt(views.PermissionUpdateDelete.as_view()),
        name='verdict_permission_update_delete'),

    url(r'pile/$', csrf_exempt(views.PileViewSet.as_view()), name='verdict_pile_view'),
    url(r'pile/vagrant/$', views.PileVagrantViewSet.as_view(), name='verdict_pile_vagrant'),
    url(r'pile/(?P<pk>\d+)/$', csrf_exempt(views.PileUpdateDeleteViewSet.as_view()),
        name='verdict_pile_update_delete'),
    url(r'pile/(?P<pk>\d+)/permission/$', csrf_exempt(views.PilePermissionViewSet.as_view()),
        name='verdict_pile_permission'),
    url(r'pile/(?P<pile_id>\d+)/permission/(?P<pk>\d+)/$', csrf_exempt(views.PilePermissionDelete.as_view()),
        name='verdict_pile_permission_delete'),

    url(r'^group/$', csrf_exempt(views.GroupViewSet.as_view()), name='verdict_group_view'),
    url(r'^group/list/$', views.GroupList.as_view(), name='verdict_group_list'),
    url(r'^group/(?P<pk>\d+)/$', csrf_exempt(views.GroupUpdate.as_view()), name='verdict_group_update_delete'),
    url(r'^group/(?P<pk>\d+)/permission/$', csrf_exempt(views.GroupPermissionViewSet.as_view()),
        name='verdict_group_permission'),
    url(r'^group/(?P<pk>\d+)/user/$', views.GroupUserList.as_view(), name='verdict_group_user_list'),
    url(r'^group/(?P<gid>\d+)/user/(?P<uid>\d+)/$', csrf_exempt(views.GroupUserViewSet.as_view()),
        name='verdict_group_user'),

    url(r'^static/(?P<path>.*)$', serve,
        {'document_root': os.path.join(os.path.dirname(__file__), 'static')}),
]

