from django.shortcuts import render
from django.views import View


# Create your views here.

class DashboardView(View):
    def get(self, request):
        context = {
            'example_data': 'Przykładowe dane do przekazania do szablonu'
        }
        return render(request, 'dashboard.html', context)

    def post(self, request):
        context = {
            'example_data': 'Przykładowe dane do przekazania do szablonu'
        }
        return render(request, 'dashboard.html', context)

def events(request):
    return render(request, 'Giveria/events.html')

def bosses(request):
    return render(request, 'Giveria/bosses.html')