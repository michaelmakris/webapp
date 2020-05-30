from django.urls import path
from . import views


urlpatterns = [
   # ex: /polls/
   path('', views.index, name='home'),
   path('mg_other/', views.mg_other, name='mg other'),
   path('mg_chf/', views.mg_chf, name='mg chf'),
   path('he_other/', views.he_other, name='mg chf'),
   path('new_scenario/', views.he_other, name='new_search'),
]