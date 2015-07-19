from django.contrib.auth.models import User
from django.test import TestCase

from trackbuild.models import Release, Build
from trackbuild.service import BuildTracker


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
        self.assertEqual(val, 'test-test-0.1.0')
        val = bt.format(build=build, nice=True)
        self.assertEqual(val, '0.1.0')
        val = bt.format(build=build, full=True) 
        self.assertEqual(val, 'test-test 0.1.0 001')
        val = bt.format(build=build, date=True)
        self.assertEqual(val, 'test-test 0.1.0 %s' % build.created)
        val = bt.format(build=build, custom='{buildno}-{major}.{minor}')
        self.assertEqual(val, '001-0.1')