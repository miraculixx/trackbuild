'''
Created on Jul 18, 2015

@author: patrick
'''
import argparse
from trackbuild.models import Release, Build, Product
from django.utils import timezone

builds = {}

class BuildTracker:
    def __init__(self, user):
        self.releases = Release.objects.all()
        self.user = user
        
    def list_builds(self, release=None, product=None):
        # if specific release given, get its builds
        for release in Release.objects.filter(name=release, user=self.user):
            (major, minor, patch) = self.get_full_version(release)
            print "Release %s.%s.%s has %d builds" % (major, minor, patch, release.builds.count())
            for build in release.builds.all():
                print self.format(release, build, full=True)
        return 'releases listed'
                
    def get_release(self, release, product=None, major=None, minor=None, patch=None):
        if isinstance(release, Release):
            return release
        z = lambda v : v if v != "+" else None
        opts = dict(major=z(major), minor=z(minor), patch=z(patch), 
                    product=product)
        opts = { k:v for k,v in opts.iteritems() if v}
        return self.releases.filter(name=release, user=self.user, 
                                    **opts).latest()
        
    def get_full_version(self, release):
        release = self.get_release(release)
        major = release.major
        minor = release.minor
        patch = release.patch
        return (major, minor, patch)
    
    def get_latest_build(self, release, major=None, minor=None, patch=None):
        release = self.get_release(release, major=major, minor=minor, 
                                   patch=patch)
        try:
            return release.builds.latest()
        except Build.DoesNotExist:
            return None
               
    def add_product(self, name=None):
        product, cr_product = Product.objects.get_or_create(name=name, 
                                                            user=self.user) 
        return product
                
    def add_release(self, release, base_release=None, product=None, 
                    major=0, minor=1, patch=0):
        if base_release:
            return Release.from_release(base_release, name=release, major=major, 
                                    minor=minor, patch=patch)
        product_opts = dict(name=product or release, user=self.user)
        product, cr_product = Product.objects.get_or_create(**product_opts) 
        release_opts = dict(name=release, major=major, 
                            minor=minor, patch=patch,
                            product=product, user=self.user)
        release, cr_release = Release.objects.get_or_create(**release_opts)
        return release
        
    def add_build(self, release=None, tag=None):
        tag = 'n/a' if not tag else tag
        if not isinstance(release, Release):
            release = Release.objects.get(name=release, user=self.user)
        build = Build.objects.create(release=release, tag=tag, user=self.user)
        return build
        
    def format(self, release=None, build=None, buildno=False, nice=True, display=False, date=False, 
               filename=False, product=None, full=False, custom=None):
        assert release or build, "need at least a build or a release object"
        # make sure we have model instances
        if release and not isinstance(release, Release):
            release = self.get_release(release)
        if build and not isinstance(build, Build):
            build = self.get_latest_build(release)
        # process
        release = release or build.release 
        build = build or self.get_latest_build(release)
        opts=dict(
            pname=product.name if product else release.product.name,
            rname=release.name,
            major=release.major,
            minor=release.minor,
            patch=release.patch,
            build=build,
            buildno="%003d" % (build.buildno if build else 0),
            builddt=build.created if build else timezone.datetime.now(),
        )
        if custom:
            return custom.format(**opts)
        fmt = ''
        if nice:
            fmt = '{major}.{minor}.{patch}'
        if display:
            fmt = '{pname}-{rname}#{major}.{minor}.{patch}'
        if full:
            fmt = "{pname}-{rname}#{major}.{minor}.{patch}#{buildno}"
        if date:
            fmt += " {builddt}"
        if buildno and not "buildno" in fmt:
            fmt = "{buildno}"
        sep = '.' if filename else ' '
        fmt = fmt.replace('#', '-' if filename else ' ')
        return sep.join(fmt.split(' ')).format(**opts)
        
    @staticmethod    
    def parseArgs(self, args):
        # get args
        parser = argparse.ArgumentParser()
        parser.add_argument("--product", "-P", help="add or set product", action="store")
        parser.add_argument("--release", "-r", help="add a release for product", action="store")
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
        args = parser.parse_args(args=args)
        return args
        
    def processArgs(self, args):
        # process
        tracker = self
        product = None
        release = None
        build = None
        if args.product:
            product = tracker.add_product(args.product)
        if not args.release:
            return (product, release, build, "No release specified")
        if not args.build and not any([args.major, args.minor, args.patch]):
            release = tracker.add_release(args.release, product=args.product)
        elif not args.build:
            base_release = product.get_latest_release(major=args.major, 
                                                      minor=args.minor, 
                                                      patch=args.patch) 
            release = tracker.add_release(args.release, base_release=base_release, 
                                          major=args.major, minor=args.minor, 
                                          patch=args.patch, product=product)
        else:
            try:
                release = self.get_release(args.release, major=args.major, 
                                                         minor=args.minor, 
                                                         patch=args.patch,
                                                         product=product)
            except Release.DoesNotExist:
                return (product, release, build, "Release not yet created. Try without --build")
            
        if args.list:
            return (product, release, build, self.list_builds(release=args.release, product=args.product))
        if args.build:
            if not args.release:
                return (product, release, build, "No release specified")
            build = tracker.add_build(release, args.tag)
            if not any([args.full, args.display, args.nice]):
                return (product, release, build, tracker.format(release, build=True))
        if not release and not build:
                return (product, release, build, "No release specified or no build created.")
        return (product, release, build, self.format(release, build, filename=args.filename, 
                           nice=args.nice, display=args.display,
                           full=args.full, date=args.date))
        
    