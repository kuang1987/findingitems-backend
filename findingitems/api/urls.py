from django.conf.urls import url, include

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .views import *

schema_view = get_schema_view(
    openapi.Info(
        title="Finding Items API",
        default_version='v1',
        description="API for finding items",
        terms_of_service="https://www.google.com/policies/terms/",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    url="%s://%s/api/" % (settings.SERVER_PROTOCOL, settings.SERVER_HOST),
)

app_name='api'
urlpatterns = [
    url(r'^doc/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^doc(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    url(r'^login/$', csrf_exempt(WechatLoginView.as_view())),
    url(r'^auth/$', csrf_exempt(UserCheckAuthView.as_view())),
    url(r'^oss_token/$', csrf_exempt(OssTokenView.as_view())),
    url(r'^instruction/', include('findingitems.api.instruction.urls'))
]