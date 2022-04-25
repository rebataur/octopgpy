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

class Field(models.Model):
    name = models.CharField(max_length=30)
    type = models.CharField(max_length=30)
    document = models.ForeignKey(Document, on_delete=models.DO_NOTHING)
    is_calculated = models.CharField(max_length=30,null=True)
    calculation_func = models.CharField(max_length=30,null=True)
    calculation_func_args = models.CharField(max_length=30,null=True)
    # models.JSONField(null=True)            


class Func(models.Model):
    name = models.CharField(max_length=30)
    body = models.CharField(max_length=1024)

class Param(models.Model):
    name = models.CharField(max_length=30) 
    paramtype =  models.CharField(max_length=30) 
    func = models.ForeignKey(Func, on_delete=models.DO_NOTHING)