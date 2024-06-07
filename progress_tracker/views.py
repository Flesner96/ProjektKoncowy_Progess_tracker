from django.shortcuts import render


# Create your views here.
def events(request):
    return render(request, 'Giveria/events.html')

def bosses(request):
    return render(request, 'Giveria/bosses.html')