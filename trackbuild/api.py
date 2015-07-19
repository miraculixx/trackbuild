from tastypie import fields
from tastypie.api import Api
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer

from trackbuild.models import Product, Release, Build


class LimitUserMixin(object):
    def obj_create(self, bundle, **kwargs):
        return super(LimitUserMixin, self).obj_create(bundle, user=bundle.request.user)

    def apply_authorization_limits(self, request, object_list):
        return object_list.filter(user=request.user)


class ProductResource(LimitUserMixin, ModelResource):
    class Meta:
        queryset = Product.objects.all()
        authentication = ApiKeyAuthentication()
        authorization = Authorization()
        resource_name = 'product'
        serializer = Serializer(formats=['json', 'jsonp'])
        always_return_data=True
        allowed_methods = ['get', 'post']
    releases = fields.ToManyField('trackbuild.api.ReleaseResource', 'releases', related_name='product', readonly=True)
        
        
class ReleaseResource(LimitUserMixin, ModelResource):
    class Meta:
        queryset = Release.objects.all()
        authentication = ApiKeyAuthentication()
        authorization = Authorization()
        resource_name = 'release'
        always_return_data=True
        allowed_methods = ['get', 'post']
    builds = fields.ToManyField('trackbuild.api.BuildResource', 'builds', related_name='release', readonly=True)
    product = fields.ToOneField('trackbuild.api.ProductResource', 'product')

        
class BuildResource(LimitUserMixin, ModelResource):
    class Meta:
        queryset = Build.objects.all()
        authentication = ApiKeyAuthentication()
        authorization = Authorization()
        resource_name = 'build'
        always_return_data=True
        allowed_methods = ['get', 'post']
    release = fields.ToOneField('trackbuild.api.ReleaseResource', 'release')
        
api_v1 = Api(api_name='v1/trackbuild')
api_v1.register(ProductResource())
api_v1.register(BuildResource())
api_v1.register(ReleaseResource())

urls = api_v1.urls