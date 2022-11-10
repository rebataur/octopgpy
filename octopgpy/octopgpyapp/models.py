from ast import Delete
from unittest.util import _MAX_LENGTH
from django.db import models

# Create your models here.
class App(models.Model):
    name = models.CharField(max_length=30)
   
class Document(models.Model):
    name = models.CharField(max_length=30)
    app = models.ForeignKey(App,on_delete=models.CASCADE)
    child_document =  models.ForeignKey(
        'Document', on_delete=models.DO_NOTHING, null=True, blank=True, related_name='sub_child')

TYPE_CHOICES = (
    ('text','text'),
    ('integer','integer'),
    ('numeric', 'numeric'),
    ('timestamp','timestamp'), 
)

class Field(models.Model):
    class Meta:
        unique_together = (('name', 'document'),)
    name = models.CharField(max_length=30,null=True,blank=True)
    descriptive_name = models.CharField(max_length=30,null=True,blank=True)
    type = models.CharField(max_length=30,default='text',choices=TYPE_CHOICES,null=True,blank=True)
    document = models.ForeignKey(Document,on_delete=models.DO_NOTHING)
    is_calculated = models.BooleanField(default=False)
    calculation_func = models.CharField(max_length=30,null=True,blank=True)
    calculation_func_args = models.CharField(max_length=30,null=True,blank=True)
    # models.JSONField(null=True)            


class Func(models.Model):
    name = models.CharField(max_length=30)
    body = models.CharField(max_length=1024)

class Param(models.Model):
    name = models.CharField(max_length=30) 
    paramtype =  models.CharField(max_length=30) 
    func = models.ForeignKey(Func, on_delete=models.DO_NOTHING)

class DocumentView(models.Model):
    name = models.CharField(max_length=30) 
    parent_document =  models.ForeignKey(
        'Document', on_delete=models.CASCADE, related_name='document_sub_child')
    parent_documentview =   models.ForeignKey('DocumentView', on_delete=models.CASCADE)
    document = models.ForeignKey(Document,on_delete=models.DO_NOTHING)

AGGREGATES = (
    ('sum','sum'),
    ('avg','avg')
)
class FromClause(models.Model):
    name = models.CharField(max_length=30) 
    dw = models.ForeignKey(DocumentView, on_delete=models.CASCADE)
    agg = models.CharField(max_length=30,choices=AGGREGATES) 

# class WhereClause(models.Model):

# class GroupByClause(models.Model):

# class HavingClause(models.Model):

# class SelectClause(models.Model):

# class OrderByClause(models.Model):

# class LimitClause(models.Model):