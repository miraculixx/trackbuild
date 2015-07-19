from django.contrib.auth.models import User
from tastypie.test import ResourceTestCase

from trackbuild.models import Release
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
        #self.api_client = ClientRequestTracer(self.api_client)
        
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
        r_release=self.deserialize(resp)
        # add a next release (release 1 => release 2)
        release = dict(product=r_product['resource_uri'], name='release 2',
                       major=1, minor=2, patch=4, previous=r_release['resource_uri'])
        resp = self.api_client.post(self.getURL("release"), format='json',
                                    data=release, 
                                    authentication=self.credentials())
        self.assertHttpCreated(resp)
        nr_release = self.deserialize(resp)
        # check previous is known (release 2 <= release 1)
        self.assertEqual(nr_release['previous'], r_release['resource_uri'])
        # check actual object relation
        m_release = Release.objects.get(pk=nr_release['id'])
        self.assertEqual(m_release.previous.pk, r_release['id'])
        self.assertEqual(m_release.previous.followers.first().pk, nr_release['id'])
        # see if the parent knows about the new release
        resp = self.api_client.get(self.getURL('release', r_release['id']), 
                                   authentication=self.credentials())
        pr_release = self.deserialize(resp)
        self.assertHttpOK(resp)
        # check follower is known to previous  (release 1 => release 2)
        self.assertEqual(pr_release['followers'], [nr_release['resource_uri']])
        
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
        self.assertHttpCreated(resp)
        
    def test_service(self):
        # new release
        result = self.service(product='test', release='test1', full=True)
        self.assertEqual(result['msg'], 'test-test1 0.1.0 000')
        self.assertEqual(result['release'], u'/api/v1/trackbuild/release/1/')
        # try a new one
        result = self.service(product='test', release='test2', full=True, 
                              filename=True)
        self.assertEqual(result['msg'], 'test-test2-0.1.0-000')
        self.assertEqual(result['release'], u'/api/v1/trackbuild/release/2/')
        # add a build
        result = self.service(product='test', release='test1', build=True, 
                              full=True, filename=True)
        self.assertEqual(result['msg'], 'test-test1-0.1.0-001')
        self.assertEqual(result['release'], u'/api/v1/trackbuild/release/1/')
        self.assertEqual(result['build'], u'/api/v1/trackbuild/build/1/')
        result = self.service(product='test', release='test1', build=True, 
                              full=True, filename=True)
        self.assertEqual(result['msg'], 'test-test1-0.1.0-002')
        self.assertEqual(result['release'], u'/api/v1/trackbuild/release/1/')
        self.assertEqual(result['build'], u'/api/v1/trackbuild/build/2/')
        # new release major
        result = self.service(product='test', release='test1', major='+', 
                              full=True, filename=True, minor=5, patch=9)
        self.assertEqual(result['msg'], 'test-test1-1.5.9-000')
        self.assertEqual(result['release'], u'/api/v1/trackbuild/release/3/')
        # add a build to the latest release
        result = self.service(product='test', release='test1', build=True, 
                              full=True, filename=True)
        self.assertEqual(result['msg'], 'test-test1-1.5.9-001')
        self.assertEqual(result['release'], u'/api/v1/trackbuild/release/3/')
        self.assertEqual(result['build'], u'/api/v1/trackbuild/build/3/')
        # add a build to an existing release
        result = self.service(product='test', release='test1', build=True, 
                              full=True, filename=True, major=0, minor=1, patch=0)
        self.assertEqual(result['msg'], 'test-test1-0.1.0-003')
        self.assertEqual(result['release'], u'/api/v1/trackbuild/release/1/')
        self.assertEqual(result['build'], u'/api/v1/trackbuild/build/4/')
        # add a new product 
        result = self.service(product='test2', release='test1',  
                              full=True, filename=True, major=0, minor=1, patch=0)
        self.assertEqual(result['msg'], 'test2-test1-0.1.0-002')
        self.assertEqual(result['release'], u'/api/v1/trackbuild/release/1/')
        self.assertEqual(result['build'], u'/api/v1/trackbuild/build/4/')
        
    def service(self, **opts):
        resp = self.api_client.get(self.getURL('service'), format='json',
                                   data=opts, 
                                   authentication=self.credentials())
        return self.deserialize(resp)