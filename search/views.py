from django.shortcuts import render
from bugs.models import Bug
from features.models import Feature
from django.db.models import Q

# Create your views here.


def search_issues(request):
    bugs = Bug.objects.filter(
        Q(name__icontains=request.GET['search_term']) | Q(description__icontains=request.GET['search_term']))
    features = Feature.objects.filter(
        Q(name__icontains=request.GET['search_term']) | Q(description__icontains=request.GET['search_term']))
    # bugs = Bug.objects.filter(name__icontains=request.GET['search_term'])

    return render(request, "searchresults.html", {"bugs": bugs, "features": features})

