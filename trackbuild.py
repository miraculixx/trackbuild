#!/usr/bin/env python
#Created on Sep 27, 2013
#@author: patrick
import argparse
import datetime
import json
import traceback

builds = {}

BUILD_LOG = '.trackbuild'

class BuildTracker:
    def __init__(self):
        self.releases = {}

    def write_log(self, filename=None):
        if not filename:
            filename = BUILD_LOG
        f = open(BUILD_LOG, 'w')
        f.write(json.dumps(self.releases))
        f.close()
        
    def read_log(self, filename=None):
        if not filename:
            filename = BUILD_LOG
        try:
            f = open(filename)
            jsondata = f.read()
            f.close()
            data = json.loads(jsondata)
            self.releases = data
        except Exception as e:
            print "Error reading %s:" % (BUILD_LOG)
            traceback.print_exc()
        return (self.releases)
    
    def init_log(self):
        self.releases = { }
        self.write_log()
    
    def list_builds(self, release=None):
        if not release:
            for release in self.releases:
                self.list_builds(release)
            return
        # if specific release given, get its builds
        builds = self.releases[release]['builds']
        (major, minor, patch) = self.get_full_version(release)
        print "Release %d.%d.%d has %d builds" % (major, minor, patch, len(builds))
        for build in builds:
            for item in build:
                print "  %s = %s" % (item, build[item])
            print '---'
                
    def get_release(self, release):
        return self.releases[release]
    
    def get_full_version(self, release):
        release = self.get_release(release)
        major = release['major']
        minor = release['minor']
        patch = release['patch']
        return (major, minor, patch)
    
    def get_latest_build(self, release):
        release = self.get_release(release)
        builds = release['builds']
        if len(builds) > 0:
            return builds[-1]
        else:
            return { 'no' : 0 }
                
    def add_release(self, release, major=0, minor=1, patch=0):
        if release in self.releases:
            raise Exception('release already registered')
        new_release = {
                       'builds' : [],
                       'major'  : major,
                       'minor'  : minor,
                       'patch'  : patch, 
        }
        self.releases[release] = new_release
        
    def add_build(self, release=None, tag=None):
        if not release:
            id = self.releases.keys()[-1]
        if not tag:
            tag = 'n/a'
        release = self.releases[release]
        builds = release['builds']
        buildno = len(builds) + 1 
        new_build = {
            'time': "%s" % datetime.datetime.now(),
            'tag' : tag,
            'no'  : buildno
        }
        builds.append(new_build)
        return (buildno, new_build)
    
    def set_version(self, release, major=None, minor=None, patch=None):
        release = self.get_release(release)
        if major:
            release['major'] = major
        if minor:
            release['minor'] = minor
        if patch:
            release['patch'] = patch

parser = argparse.ArgumentParser()
parser.add_argument("--init", "-N", help="initialize build log (discards old file!)", action="store_true")
parser.add_argument("--release", "-r", help="add a release", action="store")
parser.add_argument("--build", "-b", help="add a build log and print build no", action="store_true")
parser.add_argument("--tag", "-t", help="the build tag (eg git commit id)", action="store")
parser.add_argument("--major", "-M", help="set major version (default: 0)", action="store", type=int)
parser.add_argument("--minor", "-m", help="set minor version (default: 1)", action="store", type=int)
parser.add_argument("--patch", "-p", help="set patch number (default: 0)", action="store", type=int)
parser.add_argument("--list", "-l", help="list release(s)", action="store_true")
parser.add_argument("--nice", "-n", help="print major.minor.patch", action="store_true")
parser.add_argument("--full", "-f", help="print <release> <major.minor.patch> build <buildno>", action="store_true")
parser.add_argument("--display", "-d", help="print release major.minor.patch.build", action="store_true")
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
        print "%d.%d.%d" % (major, minor, patch)
    else:
        print "%d.%d.%d" % (major, minor, patch)
    tracker.write_log()

if args.display:
    (major, minor, patch) = tracker.get_full_version(args.release)
    build = tracker.get_latest_build(args.release)
    if args.filename:
        print "%s-%d.%d.%d" % (args.release, major, minor, patch)
    else:
        print "%s %d.%d.%d" % (args.release, major, minor, patch)
        
if args.full:
    (major, minor, patch) = tracker.get_full_version(args.release)
    build = tracker.get_latest_build(args.release)
    if args.filename:
        print "%s-%d.%d.%d.%03d" % (args.release, major, minor, patch, build['no'])
    else:
        print "%s %d.%d.%d build %03d" % (args.release, major, minor, patch, build['no'])
    
    
