import importlib
from optparse import make_option

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from util.trackbuild import TrackBuildArgs


class Command(BaseCommand):
    """
    Trackbuild command for django
    
    This is a sample client using the django internal database
    """
    args = ''
    help = 'Build management'
    option_list = BaseCommand.option_list + (
        make_option("--product", "-P", 
                    help="add or set product", action="store"),
        make_option("--release", "-r", 
                    help="add a release for product", action="store"),
        make_option("--build", "-b", 
                    help="add a build log and print build no", action="store_true"),
        make_option("--tag", "-t", 
                    help="the build tag (eg git commit id)", action="store"),
        make_option("--major", "-M", 
                    help="set major version (default: 0)", action="store"),
        make_option("--minor", "-m", 
                    help="set minor version (default: 1)", action="store"),
        make_option("--patch", "-p", 
                    help="set patch number (default: 0)", action="store"),
        make_option("--list", "-l", 
                    help="list release(s)", action="store_true"),
        make_option("--nice", "-n", default=True,
                    help="print major.minor.patch", action="store_true"),
        make_option("--full", "-f", 
                    help="print <release> <major.minor.patch> build <buildno>", action="store_true"),
        make_option("--display", "-d", 
                    help="print release major.minor.patch.build", action="store_true"),
        make_option("--date", "-D", 
                    help="print release major.minor.patch.build date", action="store_true"),
        make_option("--filename", "-i", action='store_true',
                    help="print version as release-major.minor.patch.build (use with --)")
        )

    def handle(self, *args, **options):
        service = importlib.import_module('trackbuild.service')
        user = User.objects.get(username='admin')
        bt = service.BuildTracker(user)
        args = TrackBuildArgs(options)
        product, release, build, msg = bt.processArgs(args)
        print msg
        