from uuid import uuid4

from django.contrib.auth.models import User
from django.db import models
from django.db.models import fields
from django.db.models.expressions import F, Value
from tastypie.models import create_api_key
from django.forms.models import model_to_dict

# Create your models here.
class TimestampMixin(models.Model):
    class Meta:
        abstract = True
    created = fields.DateTimeField(auto_now_add=True)
    updated = fields.DateTimeField(auto_now=True)
    
    
class Product(TimestampMixin, models.Model):
    class Meta:
        app_label = 'trackbuild'
        unique_together = ('user', 'name')
        ordering = ['user', 'name']
        get_latest_by = 'created'
    
    name = fields.CharField(max_length=50)
    #: user
    user = models.ForeignKey(User)
    
    def get_latest_release(self, major=None, minor=None, patch=None):
        z = lambda v : v if v and v != "+" else None 
        opts = dict(major=z(major), minor=z(minor), patch=z(patch))
        opts = { k:v for k,v in opts.iteritems() if v}
        try:
            return self.releases.filter(**opts).latest()
        except Release.DoesNotExist:
            pass
        try:
            return self.releases.latest()
        except:
            return None
        
    def __unicode__(self):
        return u"%s %s" % (self.user, self.name or 'unknown')
    
class Release(TimestampMixin, models.Model):
    class Meta:
        app_label = 'trackbuild'
        unique_together = ('user', 'product', 'name', 'major', 'minor', 'patch')
        ordering = ['user', 'product', 'name']
        get_latest_by = 'created'
    
    #: product 
    product = models.ForeignKey(Product, related_name='releases')
    #: release name    
    name = fields.CharField(max_length=50)
    #: major version
    major = fields.IntegerField(default=0)
    #: minor version
    minor = fields.IntegerField(default=0)
    #: patch version
    patch = fields.IntegerField(default=0)
    #: user
    user = models.ForeignKey(User)
    #: predecessor release
    previous = models.ForeignKey('Release', related_name='followers', null=True)
    
    @classmethod
    def from_release(self, release, name=None, major=0, minor=0, patch=0):
        """
        create a new release
        """
        opts=dict(name=name or release.name, product=release.product,
                  user=release.user)
        new_release = Release.objects.create(**opts)
        # check for changes to major, minor, patch
        if major == "+":
            new_release.major = release.major + 1
        elif major and (isinstance(major, int) or major.isdigit()):
            new_release.major = major 
        else:
            new_release.major = release.major
        if minor == "+":
            new_release.minor = release.minor + 1 
        elif minor and (isinstance(minor, int) or minor.isdigit()):
            new_release.minor = int(minor)
        else:
            new_release.minor = release.minor
        if patch == "+":
            new_release.patch = release.patch + 1
        elif patch and (isinstance(patch, int) or patch.isdigit()):
            new_release.patch = int(patch)
        else:
            new_release.patch = release.patch
        new_release.save()
        return new_release
    
    @property
    def text(self):
        return self.__unicode__()
    
    def __unicode__(self):
        return u"%s-%s %d.%d.%d" % (self.product, self.name, self.major, self.minor, self.patch) 
    
    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.product.name if self.product else uuid4()
        super(Release, self).save(*args, **kwargs)
        
class Build(TimestampMixin, models.Model):
    class Meta:
        app_label = 'trackbuild'
        unique_together = ('release', 'buildid')
        ordering = ['updated']
        get_latest_by = 'updated'
    
    release = models.ForeignKey(Release, related_name='builds')
    buildid = models.CharField(max_length=100, default=uuid4)
    tag = models.CharField(max_length=100)
    user = models.ForeignKey(User)
    buildno = models.IntegerField(default=0)
    
    @property
    def max_count(self):
        """ 
        get the count of builds for a given release + 1
        
        this supports concurrent access
        https://docs.djangoproject.com/en/1.7/ref/models/queries/#f-expressions
        """
        counter, created = BuildCounter.objects.get_or_create(release=self.release)
        counter.count = F('count') + 1
        counter.save()
        return BuildCounter.objects.get(release=self.release).count
    
    def save(self, *args, **kwargs):
        if not self.buildno:
            self.buildno = self.max_count
        super(Build, self).save(*args, **kwargs)
        
    def __unicode__(self):
        return u'%s %s' % (self.release, self.buildno) 
        
        
class BuildCounter(models.Model):
    """
    A simple build counter
    
    This tracks the number of builds for each release on behalf of the
    Build model.
    """
    class Meta:
        app_label = 'trackbuild'
        
    release = models.ForeignKey(Release, related_name='buildcounter')
    count = models.IntegerField(default=0)
    
    
models.signals.post_save.connect(create_api_key, sender=User)