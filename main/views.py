from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import TemplateView


class StartView(TemplateView):
    template_name = "start.html"


@method_decorator(login_required, name='dispatch')
class LoggedInView(TemplateView):
    template_name = "logged_in.html"
