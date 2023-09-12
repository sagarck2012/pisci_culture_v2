from django.urls import path

from pond_management.api.views import createPond, editPond, deletePond, listPond

urlpatterns = [
    path('create/', createPond, name='create_pond'),
    path('edit/', editPond, name='edit_pond'),
    path('delete/<int:pk>/', deletePond, name='delete_pond'),
    path('list/', listPond, name='list_pond'),
]