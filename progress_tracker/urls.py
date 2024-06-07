from django.urls import path

from progress_tracker import views

urlpatterns = [
    path('events/', views.events, name='events'),
    path('bosses/', views.bosses, name='bosses'),
]