import csv
from email import header 
import io

from msilib import datasizemask
from django.shortcuts import render,HttpResponseRedirect,reverse,get_object_or_404

from django.http import HttpResponse

from . forms import AppForm,DocumentForm,FieldForm
from . models import App,Document,Field
from django.db import connection



def index(request):
    apps = App.objects.all()
    return render(request,'octopgpyapp/index.html',context= {'apps':apps})

def showapp(request,id):
    app = App.objects.get(pk=id)
    documents = Document.objects.filter(app_id=id)
    return render(request, 'octopgpyapp/app.html', {'app': app,'documents':documents})

def newapp(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AppForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            print(form['name'])
            form.save()
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            # return HttpResponseRedirect('/')
            return HttpResponseRedirect(reverse('octopgpyapp:index'))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = AppForm()

    return render(request, 'octopgpyapp/newapp.html', {'form': form})
def documents(request,id):
    app = App.objects.get(pk=id)
    documents = Document.objects.filter(app_id=id)

    return render(request, 'octopgpyapp/documents.html', {'app': app,'documents':documents})
def newdocument(request,id):
    # if this is a POST request we need to process the form data
    app = App.objects.get(pk=id)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = DocumentForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            new_document = form.save(commit=False)
            new_document.app = app
            new_document.save()
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('octopgpyapp:documents', args=(app.id,)))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = DocumentForm()

    return render(request, 'octopgpyapp/newdocument.html', {'form': form,'app':app})

def fields(request,id,did,fid=0):

    action = request.GET.get('action')
    print(action)
    document = Document.objects.get(pk=did)
    fields = Field.objects.filter(document_id=did)
    form = None
  
    app = App.objects.get(pk=id)
    if fid:
        field = get_object_or_404(Field, id=fid)
    else:
        field = None

    print(request.method,fid,field)

    if request.method == 'POST':
        if request.FILES.get('field_file'):
            field_file = request.FILES.get('field_file')
            file = field_file.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(file))
            # Generate a list comprehension
            headers = next(reader)
            
            for header_field in headers:
                cleaned_field_file = header_field.lower().replace(' ','_').replace('.','')
                field = Field.objects.update_or_create(descriptive_name=header_field,name=cleaned_field_file,type='text',document=document)

            return HttpResponseRedirect(request.path)
      
        # check whether it's valid:
        form = FieldForm(instance=field,data=request.POST)
        if form.is_valid():
            new_field = form.save(commit=False)
            # if not fid:
            new_field.document = document
            new_field.save()
            return HttpResponseRedirect(request.path)
            # return HttpResponseRedirect(reverse('octopgpyapp:fields', args=(app.id,did,)))
    # if a GET (or any other method) we'll create a blank form
    elif action == 'edit':
        field = Field.objects.get(pk=fid)
        form = FieldForm(instance=field)
    elif action == 'delete':
        Field.objects.get(pk=fid).delete()
        return HttpResponseRedirect(reverse('octopgpyapp:fields', args=(app.id,did,)))
    elif action == 'generate':
        generate_document_db(did)
        return HttpResponseRedirect(reverse('octopgpyapp:fields', args=(app.id,did,)))
    elif action == 'delete_all':
        Field.objects.all().delete()
    else:
        form = FieldForm()

    return render(request, 'octopgpyapp/fields.html', context={'app':app,'document':document, 'fields':fields,'form':form,'fid':fid})


def appdocument(request,id,did):
    # if this is a POST request we need to process the form data
    app = App.objects.get(pk=id)
    document = Document.objects.get(pk=did)

    
    
    document_data = f"select * from {app.name}_{document.name} limit 10" 
    cols,res = fetch_sql_cmd(document_data)
    print(document_data,res)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = DocumentForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            new_document = form.save(commit=False)
            new_document.app = app
            new_document.save()
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('octopgpyapp:appdocument', args=(app.id,)))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = DocumentForm()

    return render(request, 'octopgpyapp/appdocument.html', {'form': form,'app':app,'document':document,'cols':cols,'res':res})

def newentry(request,id,did):
    # if this is a POST request we need to process the form data
    app = App.objects.get(pk=id)
    document = Document.objects.get(pk=did)
    fields = Field.objects.filter(document_id=did)
    # generate_document_db(did)
    if request.method == 'POST':    
        print(request.FILES)
        if request.FILES.get('newentry_file'):
            field_file = request.FILES.get('newentry_file')
            file = field_file.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(file))
            # Generate a list comprehension
            headers = next(reader)           
            
            for line in reader:
                print(line)
                f_names = []
                f_vals = []
               
                for f in fields:
                    print(f.name)
                    # if not f.is_calculated or f.name != 'file_name':                        
                    
                    
                    if f.descriptive_name != 'File Name' and not f.is_calculated :
                        f_names.append(f.name)
                        val = line[f.descriptive_name].replace("'","''")                       
                        if f.type != "numeric" and f.type != 'int':
                            f_vals.append(f"'{val}'")                    
                        else:
                            f_vals.append(val)
                f_names.append("file_name")
                f_vals.append(f"'{field_file.name}'")
                sql = f"insert into {app.name}_{document.name}({','.join(f_names)}) values({','.join(f_vals)})"
                execute_sql_cmd(sql)

            return HttpResponseRedirect(request.path)
        # create a form instance and populate it with data from the request:
        data = request.POST
       
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print(data,fields)
        f_names = []
        f_vals = []
        for f in fields:
            if not f.is_calculated:
                f_names.append(f.name)
                if f.type != "numeric":
                    f_vals.append(f"'{data[f.name]}'")
                else:
                    f_vals.append(data[f.name])
                
        sql = f"insert into {app.name}_{document.name}({','.join(f_names)}) values({','.join(f_vals)})"
        print(sql,f_names,f_vals)
        execute_sql_cmd(sql)
        return HttpResponseRedirect(request.path)
    # if a GET (or any other method) we'll create a blank form
    else:
        form = DocumentForm()

    return render(request, 'octopgpyapp/newentry.html', {'form': form,'app':app,'document':document,'fields':fields})

def generate_document_db(did):
    document = Document.objects.get(pk=did)
    app = document.app
    fields = Field.objects.filter(document_id=did)
    print("====================")
    print(document,app,fields)   

    # create empty table
    table_name = f"{app.name}_{document.name}"
    sql = f"create table if not exists {table_name}();"    
    print(sql)
    execute_sql_cmd(sql)
    
    f = []
    for field in fields:
        # field.type = 'text' if not field.type else field.type
        if field.is_calculated:
            f.append(f"alter table {table_name}  add if not exists {field.name} {field.type} GENERATED ALWAYS AS ({field.calculation_func}({field.calculation_func_args})) stored")
        else:
            f.append(f"alter table {table_name}  add if not exists {field.name} {field.type}")
    print(f)
    alter_table_cmds = ';'.join(f)
    print(alter_table_cmds)
    execute_sql_cmd(alter_table_cmds)

def execute_sql_cmd(sql):
    print(sql)
    with connection.cursor() as cursor:
        cursor.execute(sql)
   

def fetch_sql_cmd(sql):
    print(sql)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
        cols = [col[0] for col in cursor.description]
    return cols,rows