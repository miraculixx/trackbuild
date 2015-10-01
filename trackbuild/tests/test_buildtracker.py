from django.contrib.auth.models import User
from django.test import TestCase

from trackbuild.models import Release, Build
from trackbuild.service import BuildTracker
from util.trackbuild import TrackBuildArgs


# Create your tests here.
class BuildTrackerTests(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        self.user = User.objects.create_user('user', 'test')
        self.bt = BuildTracker(self.user)
        
    def tearDown(self):
        TestCase.tearDown(self)
        
    def test_add_release(self):
        bt = self.bt
        release = bt.add_release('test', major=1, minor=2, patch=3)
        self.assertIsInstance(release, Release)
        self.assertEqual(release.major, 1)
        self.assertEqual(release.minor, 2)
        self.assertEqual(release.patch, 3)
        self.assertEqual(release.builds.count(), 0)
                
    def test_add_build(self):
        bt = self.bt
        bt.add_release('test')
        build = bt.add_build('test')
        self.assertIsInstance(build, Build)
        self.assertEqual(build.buildno, 1)
        build = bt.add_build('test')
        self.assertEqual(build.buildno, 2)
        self.assertEqual(build.release.builds.count(), 2)
        self.assertEqual(build.max_count, 3)
        
    def test_format(self):
        bt = self.bt
        bt.add_release('test')
        build = bt.add_build('test')
        val = bt.format(build=build, display=True)
        self.assertEqual(val, 'test-test 0.1.0')
        val = bt.format(build=build, display=True, filename=True)
        self.assertEqual(val, 'test-test-0.1.0')
        val = bt.format(build=build, nice=True)
        self.assertEqual(val, '0.1.0')
        val = bt.format(build=build, full=True) 
        self.assertEqual(val, 'test-test 0.1.0 001')
        val = bt.format(build=build, date=True, display=True)
        self.assertEqual(val, 'test-test 0.1.0 %s' % build.created)
        val = bt.format(build=build, date=True)
        self.assertEqual(val, '0.1.0 %s' % build.created)
        val = bt.format(build=build, custom='{buildno}-{major}.{minor}')
        self.assertEqual(val, '001-0.1')
        
    def test_add_by_args(self):
        product, release, build, msg = self.service(product='test1', 
                                                    release='test1')
        self.assertEqual(product.name, 'test1')
        self.assertEqual(release.name, 'test1')
        product, release, build, msg = self.service(product='test1', 
                                                    release='test1',
                                                    major="+")
        self.assertEqual(product.name, 'test1')
        self.assertEqual(release.name, 'test1')
        self.assertEqual(release.major, 1)
        self.assertEqual(release.builds.count(), 0)
        product, release, build, msg = self.service(product='test1', 
                                                    release='test1',
                                                    minor="+")
        self.assertEqual(release.major, 1)
        self.assertEqual(release.minor, 2)
        product, release, build, msg = self.service(product='test1', 
                                            release='test1',
                                            patch="+")
        self.assertEqual(release.major, 1)
        self.assertEqual(release.minor, 2)
        self.assertEqual(release.patch, 1)
        product, release, build, msg = self.service(product='test1', 
                                            release='test1',
                                            major='+',
                                            minor='+',
                                            patch="+")
        self.assertEqual(release.major, 2)
        self.assertEqual(release.minor, 3)
        self.assertEqual(release.patch, 2)
        
    def test_select_specific_release(self):
        # add a first release
        product, release, build, msg = self.service(product='test1', 
                                            release='test1')
        self.assertEqual(release.major, 0)
        self.assertEqual(release.minor, 1)
        self.assertEqual(release.patch, 0)
        # add a new release
        product, release, build, msg = self.service(product='test1', 
                                            release='test1', major="+")
        self.assertEqual(release.major, 1)
        self.assertEqual(release.minor, 1)
        self.assertEqual(release.patch, 0)
        # add a build to the first release
        product, release, build, msg = self.service(product='test1', 
                                            release='test1',
                                            major=0,
                                            minor=1,
                                            patch=0, build=True)
        self.assertEqual(release.major, 0)
        self.assertEqual(release.minor, 1)
        self.assertEqual(release.patch, 0)
        self.assertEqual(release.builds.count(), 1)
        
    def test_get_release_version(self):
        # add a first release
        product, release, build, msg = self.service(product='product1', 
                                            release='test1')
        self.assertEqual(release.product.name, product.name)
        self.assertEqual(product.name, 'product1')
        self.assertEqual(release.major, 0)
        self.assertEqual(release.minor, 1)
        self.assertEqual(release.patch, 0)
        # check what we have
        product, release, build, msg = self.service(product='product1', 
                                            release='test1')
        self.assertEqual(msg, '')
        self.assertEqual(release.major, 0)
        self.assertEqual(release.minor, 1)
        self.assertEqual(release.patch, 0)
        
    def test_add_twice(self):
        # add a first release
        product, release, build, msg = self.service(product='product1', 
                                            release='test1')
        self.assertEqual(release.product.name, product.name)
        self.assertEqual(product.name, 'product1')
        self.assertEqual(release.major, 0)
        self.assertEqual(release.minor, 1)
        self.assertEqual(release.patch, 0)
        # add a new release
        product, release, build, msg = self.service(product='product1', 
                                            release='test1', major="+")
        self.assertEqual(release.product.name, product.name)
        self.assertEqual(product.name, 'product1')
        self.assertEqual(release.major, 1)
        self.assertEqual(release.minor, 1)
        self.assertEqual(release.patch, 0)
        # add a new release
        product, release, build, msg = self.service(product='product1', 
                                            release='test1', minor="+")
        self.assertEqual(release.product.name, product.name)
        self.assertEqual(product.name, 'product1')
        self.assertEqual(release.major, 1)
        self.assertEqual(release.minor, 2)
        self.assertEqual(release.patch, 0)
        
    def test_add_specific(self):
        # add a specific release
        product, release, build, msg = self.service(product='product1', 
                                            release='test1', major=5)
        self.assertEqual(release.product.name, product.name)
        self.assertEqual(product.name, 'product1')
        self.assertEqual(release.major, 5)
        self.assertEqual(release.minor, 0)
        self.assertEqual(release.patch, 0)
        # add a specific minor release 
        product, release, build, msg = self.service(product='product1', 
                                            release='test1', major=5, minor=1)
        self.assertEqual(release.product.name, product.name)
        self.assertEqual(product.name, 'product1')
        self.assertEqual(release.major, 5)
        self.assertEqual(release.minor, 1)
        self.assertEqual(release.patch, 0)
        
        
    def service(self, **options):
        args = TrackBuildArgs(options)
        return self.bt.processArgs(args)
        