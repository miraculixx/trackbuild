'''
Created on Jul 18, 2015

@author: patrick
'''
#!/usr/bin/env python
#Created on Sep 27, 2013
#@author: patrick
import argparse
import datetime
from trackbuild.models import Release, Build, Product

builds = {}

class BuildTracker:
    def __init__(self, user):
        self.releases = Release.objects.all()
        self.user = user
        
    def list_builds(self, release=None):
        if not release:
            for release in self.releases:
                self.list_builds(release)
            return
        # if specific release given, get its builds
        builds = self.releases.filter(name=release).builds.all()
        (major, minor, patch) = self.get_full_version(release)
        print "Release %s.%s.%s has %d builds" % (major, minor, patch, len(builds))
        for build in builds:
            for item in build:
                print "  %s = %s" % (item, build[item])
            print '---'
                
    def get_release(self, release):
        return self.releases.get(name=release)
    
    def get_full_version(self, release):
        release = self.get_release(release)
        major = release.major
        minor = release.minor
        patch = release.patch
        return (major, minor, patch)
    
    def get_latest_build(self, release):
        release = self.get_release(release)
        builds = release.builds.all()
        if len(builds) > 0:
            return builds.latest()
        else:
            return None
               
    def add_product(self, name=None):
        product, cr_product = Product.objects.get_or_create(name=name) 
        if not cr_product:
            raise Exception('release already registered')
        return product
                
    def add_release(self, release, product=None, major=0, minor=1, patch=0):
        product_opts = dict(name=product or release, user=self.user)
        product, cr_product = Product.objects.get_or_create(**product_opts) 
        release_opts = dict(name=release, major=major, 
                            minor=minor, patch=patch,
                            product=product, user=self.user)
        release, cr_release = Release.objects.get_or_create(**release_opts)
        if not cr_release:
            raise Exception('release already registered')
        release.major = major
        release.minor = minor 
        release.patch = patch
        release.save()
        return release
        
    def add_build(self, release=None, tag=None):
        if not tag:
            tag = 'n/a'
        release = self.releases.get(name=release)
        build = Build.objects.create(release=release, tag=tag, user=self.user)
        return build
    
    def set_version(self, release, major=None, minor=None, patch=None):
        release = self.get_release(release)
        if major == "+":
            release.major += 1 
        if minor == "+":
            release.minor += 1
        if patch == "+":
            release.patch += 1
        if major:
            release.major = int(major)
        if minor:
            release.minor = int(minor)
        if patch:
            release.patch = int(patch)
        release.save()
        return release
    
    def format(self, release=None, build=None, buildno=False, nice=False, display=False, date=False, 
               filename=False, product=None, full=False, custom=None):
        assert release or build, "need at least a build or a release object"
        release = release or build.release 
        build = build or release.get_latest_build()
        opts=dict(
            pname=product.name if product else release.product.name,
            rname=release.name,
            major=release.major,
            minor=release.minor,
            patch=release.patch,
            build=build,
            buildno="%003d" % (build.buildno if build else 0),
            builddt=build.created if build else datetime.datetime(),
        )
        if buildno:
            return "{build_count}".format(**opts)
        if nice:
            if filename:
                return "{major}.{minor}.{patch}".format(**opts)
            return "{major}.{minor}.{patch}".format(**opts)
        if display:
            if filename:
                return "{pname}-{rname}-{major}.{minor}.{patch}".format(**opts)
            return "{pname}-{rname}-{major}.{minor}.{patch}".format(**opts)
        if full:
            if filename:
                return "{pname}-{rname}-{major}.{minor}.{patch}.{buildno}".format(**opts)
            return "{pname}-{rname} {major}.{minor}.{patch} {buildno}".format(**opts)
        if date:
            if filename:
                return "{pname}-{rname}-{major}.{minor}.{patch}.{builddt}".format(**opts)
            return "{pname}-{rname} {major}.{minor}.{patch} {builddt}".format(**opts)
        if custom:
            return custom.format(**opts)
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", "-N", help="initialize build log (discards old file!)", action="store_true")
    parser.add_argument("--release", "-r", help="add a release", action="store")
    parser.add_argument("--build", "-b", help="add a build log and print build no", action="store_true")
    parser.add_argument("--tag", "-t", help="the build tag (eg git commit id)", action="store")
    parser.add_argument("--major", "-M", help="set major version (default: 0)", action="store")
    parser.add_argument("--minor", "-m", help="set minor version (default: 1)", action="store")
    parser.add_argument("--patch", "-p", help="set patch number (default: 0)", action="store")
    parser.add_argument("--list", "-l", help="list release(s)", action="store_true")
    parser.add_argument("--nice", "-n", help="print major.minor.patch", action="store_true")
    parser.add_argument("--full", "-f", help="print <release> <major.minor.patch> build <buildno>", action="store_true")
    parser.add_argument("--display", "-d", help="print release major.minor.patch.build", action="store_true")
    parser.add_argument("--date", "-D", help="print release major.minor.patch.build date", action="store_true")
    parser.add_argument("--filename", "-i", help="print version as release-major.minor.patch.build (use with --full, --display, --nice)", action="store_true")
    args = parser.parse_args()
    
    tracker = BuildTracker()
    
    if args.init:
        tracker.init_log()
        tracker.write_log()
    else:
        tracker.read_log()
        
    if args.release:
        if not args.release in tracker.releases:
            tracker.add_release(args.release)
            tracker.write_log()
        
    if args.list:
        release = args.release
        tracker.list_builds(release=release)
        
    
    
    if args.build:
        if not args.release:
            print "No release specified"
            exit()
        (buildno, build) = tracker.add_build(args.release, args.tag)
        tracker.write_log()
        if not args.full and not args.display and not args.nice:
            print "%003d" % buildno
    
    if args.major:
        if not args.release:
            print "No release specified"
            exit()
        tracker.set_version(args.release, major=args.major)
        tracker.write_log()
        
    if args.minor:
        if not args.release:
            print "No release specified"
            exit()
        tracker.set_version(args.release, minor=args.minor)
        tracker.write_log()
        
    if args.patch:
        if not args.release:
            print "No release specified"
            exit()
        tracker.set_version(args.release, patch=args.patch)
        tracker.write_log()
        
    if args.nice:
        (major, minor, patch) = tracker.get_full_version(args.release)
        if args.filename:
            print "%s.%s.%s" % (major, minor, patch)
        else:
            print "%s.%s.%s" % (major, minor, patch)
    
    if args.display:
        (major, minor, patch) = tracker.get_full_version(args.release)
        build = tracker.get_latest_build(args.release)
        if args.filename:
            print "%s-%s.%s.%s" % (args.release, major, minor, patch)
        else:
            print "%s %s.%s.%s" % (args.release, major, minor, patch)
            
    if args.full:
        (major, minor, patch) = tracker.get_full_version(args.release)
        build = tracker.get_latest_build(args.release)
        if args.filename:
            print "%s-%s.%s.%s.%03d" % (args.release, major, minor, patch, build['no'])
        else:
            print "%s %s.%s.%s build %03d" % (args.release, major, minor, patch, build['no'])
        
    if args.date:
        (major, minor, patch) = tracker.get_full_version(args.release)
        build = tracker.get_latest_build(args.release)
        if 'date' in build:
            date = build['date']
        else:
            date = "(no date)"
        if args.filename:
            print "%s-%s.%s.%s-%s" % (args.release, major, minor, patch, date)
        else:
            print "%s %s.%s.%s %s" % (args.release, major, minor, patch, date)
        
