from django.shortcuts import render,HttpResponseRedirect,reverse

from django.http import HttpResponse

from . forms import AppForm,DocumentForm,FieldForm
from . models import App,Document,Field

def index(request):
    apps = App.objects.all()
    return render(request,'octopgpyapp/index.html',context= {'apps':apps})

def showapp(request,id):
    app = App.objects.get(pk=id)

    return render(request, 'octopgpyapp/app.html', {'app': app})

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

def fields(request,id,did):
    document = Document.objects.get(pk=did)
    fields = Field.objects.filter(document_id=did)
  
    app = App.objects.get(pk=id)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = FieldForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            new_field = form.save(commit=False)
            new_field.document = document
            new_field.save()
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('octopgpyapp:fields', args=(app.id,did,)))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = FieldForm()

    return render(request, 'octopgpyapp/fields.html', context={'app':app,'document':document, 'fields':fields,'form':form})
