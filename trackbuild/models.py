from uuid import uuid4

from django.contrib.auth.models import User
from django.db import models
from django.db.models import fields
from django.db.models.expressions import F, Value
from tastypie.models import create_api_key

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
    
    name = fields.CharField(max_length=50)
    #: user
    user = models.ForeignKey(User)
    
    
class Release(TimestampMixin, models.Model):
    class Meta:
        app_label = 'trackbuild'
        unique_together = ('user', 'product')
        ordering = ['user', 'product', 'name']
    
    #: product 
    product = models.ForeignKey(Product, related_name='releases')
    #: release name    
    name = fields.CharField(max_length=50)
    #: major version
    major = fields.IntegerField()
    #: minor version
    minor = fields.IntegerField()
    #: patch version
    patch = fields.IntegerField()
    #: user
    user = models.ForeignKey(User)
    
        
class Build(TimestampMixin, models.Model):
    class Meta:
        app_label = 'trackbuild'
        unique_together = ('release', 'buildid')
        ordering = ['updated']
    
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