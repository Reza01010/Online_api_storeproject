from django.shortcuts import render
from django.views.generic import TemplateView
from cart.tasks import add__,add_

class HomePageView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Call Celery task asynchronously
        add__.delay(1, 2)
        add_(1,2)
        
        return context


class AboutUsPagesView(TemplateView):
    template_name = 'pages/aboutus.html'


