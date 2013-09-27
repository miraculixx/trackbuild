trackbuild
========

a simple build tracker

Ever had the problem to increase build numbers?                   
or version numbers?
or file names made of something like release-major.minor.patch.build.tgz?

trackbuild solves this problem once and for all.

###Setup

1. copy trackbuild.py into your project directory and create an alias to trackbuild

        cp trackbuild.py /my/project
        alias trackbuild='./trackbuild.py'

2. initialize the log file (.trackbuild)        

        trackbuild -N

3. add your first release

        trackbuild -r alpha

  This will create the alpha release, with major.minor.patch set to 0.1.0. The command will not print any output at this point.

4. Add a build

        #trackbuild -r alpha -b
        001

    You have now added the first build to release alpha. trackbuild incremenes the build number and prints it as a 3-character string. 

###Listing builds

You can show details like so:

        #trackbuild -r alpha -l
        Release 0.1.0 has 6 builds
        tag = n/a
        no = 1
        time = 2013-09-27 13:16:45.147788
        ---

###Automatically keep track of builds

In your builds, increase the build number with a simple call to trackbuild:

       #trackbuild -r alpha -b
       002

Use the output string as the build number in your downstream build scripts. trackbuild outputs a full version string if that's what you need:

         #trackbuild -r alpha -b --full
         test 0.1.0 build 002

        #trackbuild -r alpha -b --full --filename
        test-0.1.0.002

See the discussion below for details on printing version numbers.
                 
### Print version strings

Print major.minor.patch string

        #trackbuild -r alpha --nice
        0.1.0

Print release major.minor.patch string

        #trackbuild -r alpha --nice
        0.1.0

Print release major.minor.patch build nnn

       #trackbuild -r alpha --full
       alpha 0.1.0 build 001

Print release major.minor.patch (no build number)

       #trackbuild -r alpha --display
       alpha 0.1.0


###Print file names

Often times we need the release information as a filename. To do so, pass --filename (or -i) along with any of the above --nice, --full, --display arguments:

        #trackbuild -r alpha --nice --filename
        0.1.0

        #trackbuild -r alpha --full --filename
        alpha-0.1.0.000

        #trackbuild -r alpha --display --filename
        alpha-0.1.0

###Set major, minor and patch versions

Setting any of the version components is simple:

        #trackbuild -r alpha -M 1 -m 2 -p 5 --full
        alpha 1.2.5 build 001

###Help       
```
#trackbuild -h
usage: trackbuild.py [-h] [--init] [--release RELEASE] [--build] [--tag TAG]
                     [--major MAJOR] [--minor MINOR] [--patch PATCH] [--list]
                     [--nice] [--full] [--display] [--filename]

optional arguments:
  -h, --help            show this help message and exit
  --init, -N            initialize build log (discards old file!)
  --release RELEASE, -r RELEASE
                        add a release
  --build, -b           add a build log and print build no
  --tag TAG, -t TAG     the build tag (eg git commit id)
  --major MAJOR, -M MAJOR
                        set major version (default: 0)
  --minor MINOR, -m MINOR
                        set minor version (default: 1)
  --patch PATCH, -p PATCH
                        set patch number (default: 0)
  --list, -l            list release(s)
  --nice, -n            print major.minor.patch
  --full, -f            print <release> <major.minor.patch> build <buildno>
  --display, -d         print release major.minor.patch.build
  --filename, -i        print version as release-major.minor.patch.build (use
                        with --full, --display, --nice)
```


###Licence

trackbuild is covered by the MIT license.
(c) 2013 Patrick Senti 


        



       
