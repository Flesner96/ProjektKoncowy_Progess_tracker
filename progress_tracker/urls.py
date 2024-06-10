from django.urls import path

from progress_tracker import views
from progress_tracker.views import DashboardView

urlpatterns = [
    path('events/', views.events, name='events'),
    path('bosses/', views.bosses, name='bosses'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]