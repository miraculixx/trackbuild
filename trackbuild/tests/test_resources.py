from django.contrib.auth.models import User
from tastypie.test import ResourceTestCase

from util.clienttrace import ClientRequestTracer


class ResourceTests(ResourceTestCase):
    def setUp(self):
        ResourceTestCase.setUp(self)
        self.username = 'test'
        self.password = 'pass'
        self.user = User.objects.create_user(self.username, 
                                             'test@trackbuild.ch', 
                                             self.password)
        self.URL = '/api/v1/trackbuild'
        self.api_client = ClientRequestTracer(self.api_client)
        
    def tearDown(self):
        ResourceTestCase.tearDown(self)
        
    def credentials(self):
        return self.create_apikey(self.username, self.user.api_key.key)
        
    def getURL(self, resource, pk=None):
        if pk:
            return "%s/%s/%s/" % (self.URL, resource, pk)
        return "%s/%s/" % (self.URL, resource)

    def test_product_resource(self):
        resp = self.api_client.get(self.getURL("product"), format='json', 
                                   authentication=self.credentials())
        self.assertHttpOK(resp)
        product=dict(name='test')
        resp = self.api_client.post(self.getURL("product"), format='json',
                                    data=product, 
                                    authentication=self.credentials())
        self.assertHttpCreated(resp)
        
    def test_release_resource(self):
        # create a product
        resp = self.api_client.get(self.getURL("product"), format='json', 
                                   authentication=self.credentials())
        self.assertHttpOK(resp)
        product=dict(name='test')
        resp = self.api_client.post(self.getURL("product"), format='json',
                                    data=product, 
                                    authentication=self.credentials())
        self.assertHttpCreated(resp)
        r_product = self.deserialize(resp)
        # add a release
        release = dict(product=r_product['resource_uri'], name='release',
                       major=1, minor=2, patch=3)
        resp = self.api_client.post(self.getURL("release"), format='json',
                                    data=release, 
                                    authentication=self.credentials())
        self.assertHttpCreated(resp)
        
    def test_build_resource(self):
        # create a product
        resp = self.api_client.get(self.getURL("product"), format='json', 
                                   authentication=self.credentials())
        self.assertHttpOK(resp)
        product=dict(name='test')
        resp = self.api_client.post(self.getURL("product"), format='json',
                                    data=product, 
                                    authentication=self.credentials())
        self.assertHttpCreated(resp)
        r_product = self.deserialize(resp)
        # add a release
        release = dict(product=r_product['resource_uri'], name='release',
                       major=1, minor=2, patch=3)
        resp = self.api_client.post(self.getURL("release"), format='json',
                                    data=release, 
                                    authentication=self.credentials())
        self.assertHttpCreated(resp)
        r_release = self.deserialize(resp)
        # add a build
        release = dict(release=r_release['resource_uri'], tag='some build tag')
        resp = self.api_client.post(self.getURL("build"), format='json',
                                    data=release, 
                                    authentication=self.credentials())
        print resp
        self.assertHttpCreated(resp)
        
        