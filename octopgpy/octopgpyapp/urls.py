from django.urls import path

from . import views
app_name = 'octopgpyapp'
urlpatterns = [
    path('', views.index, name='index'),
    path('app/<int:id>/', views.showapp, name='showapp'),
    path('app/new/', views.newapp, name='newapp'),   
    path('app/<int:id>/documents/', views.documents, name='documents'),
    path('app/<int:id>/newdocument/', views.newdocument, name='newdocument'),

    path('app/<int:id>/document/<int:did>/fields', views.fields, name='fields'),
]