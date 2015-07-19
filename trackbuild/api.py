from django.conf.urls import url
from tastypie import fields
from tastypie.api import Api
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.resources import ModelResource, Resource
from tastypie.serializers import Serializer

from trackbuild.models import Product, Release, Build
from trackbuild.service import BuildTracker
from util.trackbuild import TrackBuildArgs


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
    previous = fields.ToOneField('trackbuild.api.ReleaseResource', 'previous', null=True)
    text = fields.CharField('text', readonly=True)
    followers = fields.ListField(readonly=True)
    
    def dehydrate(self, bundle):
        child_resources = bundle.data.get('followers') or []
        for child in bundle.obj.followers.all():
            child_resources.append(self.get_resource_uri(child))
        bundle.data['followers'] = child_resources
        return bundle
        
class BuildResource(LimitUserMixin, ModelResource):
    class Meta:
        queryset = Build.objects.all()
        authentication = ApiKeyAuthentication()
        authorization = Authorization()
        resource_name = 'build'
        always_return_data=True
        allowed_methods = ['get', 'post']
    release = fields.ToOneField('trackbuild.api.ReleaseResource', 'release')
   
        
class TrackBuildResource(Resource):
    class Meta:
        authentication = ApiKeyAuthentication()
        authorization = Authorization()
        resource_name = 'service'
        always_return_data=True
        allowed_methods = ['get']
    
    def get_list(self, request, **kwargs):
        bundle = self.build_bundle(request=request, data=request.GET)
        bt = BuildTracker(bundle.request.user)
        args = TrackBuildArgs(bundle.data)
        product, release, build, msg = bt.processArgs(args)
        result = {
           'msg' : msg,
        }
        if product:
            result['product'] = ProductResource().get_resource_uri(product)
        if release:
            result['release'] = ReleaseResource().get_resource_uri(release)
        if build:
            result['build']  = BuildResource().get_resource_uri(build)
        return self.create_response(request, result) 
    
api_v1 = Api(api_name='v1/trackbuild')
api_v1.register(ProductResource())
api_v1.register(BuildResource())
api_v1.register(ReleaseResource())
api_v1.register(TrackBuildResource())

urls = api_v1.urls