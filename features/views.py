import json

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone

from .models import Feature
from django.views.generic import DateDetailView
from django.http import HttpResponse, HttpResponseNotAllowed
from .forms import FeatureForm

# Create your views here.


def all_features(request):
    """
    Creates a view that returns a list of all
    Features and renders them to the 'features.html' template
    """
    features = Feature.objects.all()
    return render(request, "features.html", {"features": features})


def feature_detail(request, pk):
    """
    Creates a view that returns a single
    Feature object based on the feature ID (pk) and
    renders it to the 'featuredetail.html' template.
    Return 404 if not found
    """
    feature = get_object_or_404(Feature, pk=pk)
    feature.views += 1
    feature.save()
    return render(request, "featuredetail.html", {'feature': feature})


class FeatureDetailView(DateDetailView):
    model = Feature
    date_field = "date_added"
    month_format = "%m"

    def get_context_data(self, **kwargs):
        context = super(FeatureDetailView, self).get_context_data(**kwargs)
        context.update({'next': reverse('comments-xtd-sent')})
        return context


@login_required()
def add_or_edit_feature(request, pk=None):
    """
    Create a view that allows to add
    or edit a feature depending if the feature ID
    is null or not. A user should only be able
    to edit a feature if they created it, or if they
    are staff
    """
    feature = get_object_or_404(Feature, pk=pk) if pk else None
    print(feature)
    if request.method == "POST":
        form = FeatureForm(request.POST, files=request.FILES, instance=feature)
        if form.is_valid():
            if feature is None:
                feature = form.save(commit=False)
                feature.username = request.user
                feature.save()
                return redirect(feature_detail, feature.pk)
            else:
                if request.user.is_staff or request.user == feature.username:
                    feature = form.save(commit=False)
                    feature.save()
                    return redirect(feature_detail, feature.pk)
                else:
                    return HttpResponse(status=403)
    else:
        if feature is None or request.user.is_staff or request.user == feature.username:
            form = FeatureForm(instance=feature)
        else:
            return HttpResponse(status=403)
    return render(request, 'featureform.html', {'form': form})


def update_status(request):
    """
        Create a view that allows a user to update the status of an issue
    """
    if request.method == "POST":
        data = json.loads(request.body)

        feature = get_object_or_404(Feature, pk=data['id'])
        # Check if the status is different
        if feature.status == data['status']:
            print('status stayed the same')
            return HttpResponse(status=204)

        if data['status'] == 'IN PROGRESS':
            if feature.date_started is None:
                feature.date_started = timezone.now()

        elif data['status'] == 'COMPLETE':
            feature.date_finished = timezone.now()

        elif feature.status == 'COMPLETE':
            feature.date_finished = None

        feature.status = data['status']
        print(feature.status)
        feature.save()
        return HttpResponse(status=204)
    else:
        return HttpResponseNotAllowed(["POST"])
