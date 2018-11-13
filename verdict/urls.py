import os
from django.conf.urls import url
from django.views.static import serve

from . import views


urlpatterns = [
    url(r'^user/$', views.UserTemplate.as_view(), name='verdict_user_view'),

    url(r'^permission/$', views.PermissionViewSet.as_view(), name='verdict_permission_view'),
    url(r'^permission/(?P<pk>\d+)/$', views.PermissionUpdateDelete.as_view(),
        name='verdict_permission_update_delete'),

    url(r'pile/$', views.PileViewSet.as_view(), name='verdict_pile_view'),
    url(r'pile/vagrant/$', views.PileVagrantViewSet.as_view(), name='verdict_pile_vagrant'),
    url(r'pile/(?P<pk>\d+)/$', views.PileUpdateDeleteViewSet.as_view(), name='verdict_pile_update_delete'),
    url(r'pile/(?P<pk>\d+)/permission/$', views.PilePermissionViewSet.as_view(), name='verdict_pile_permission'),
    url(r'pile/(?P<pile_id>\d+)/permission/(?P<pk>\d+)/$', views.PilePermissionDelete.as_view(),
        name='verdict_pile_permission_delete'),

    url(r'^group/$', views.GroupViewSet.as_view(), name='verdict_group_view'),
    url(r'^group/list/$', views.GroupList.as_view(), name='verdict_group_list'),
    url(r'^group/(?P<pk>\d+)/$', views.GroupUpdate.as_view(), name='verdict_group_update_delete'),
    url(r'^group/(?P<pk>\d+)/permission/$', views.GroupPermissionViewSet.as_view(),
        name='verdict_group_permission'),
    url(r'^group/(?P<pk>\d+)/user/$', views.GroupUserList.as_view(), name='verdict_group_user_list'),
    url(r'^group/(?P<gid>\d+)/user/(?P<uid>\d+)/$', views.GroupUserViewSet.as_view(), name='verdict_group_user'),

    url(r'^static/(?P<path>.*)$', serve,
        {'document_root': os.path.join(os.path.dirname(__file__), 'static')}),
]

