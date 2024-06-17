from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy

from .models import Category, News
from .forms import ContactForm, CommentForm
from django.views.generic import TemplateView, ListView, UpdateView, DeleteView, CreateView
from news_project.custom_permissions import OnlyLoggedSuperUser
from hitcount.views import HitCountMixin
from hitcount.utils import get_hitcount_model

# Create your views here.

def news_list(request):
    news_list = News.objects.filter(status=News.Status.Published)
    context = {
        "news_list": news_list
    }
    return render(request, "news/news_list.html", context)

def news_detail(request, news):
    news = get_object_or_404(News, slug=news, status=News.Status.Published)
    context = {}
    hit_count = get_hitcount_model().objects.get_for_object(news)
    hits = hit_count.hits
    hitcontext = context['hitcount'] = {'pk': hit_count.pk}
    hit_count_response = HitCountMixin.hit_count(request, hit_count)
    if hit_count_response.hit_counted:
        hits = hits + 1
        hitcontext['hit_counted'] = hit_count_response.hit_counted
        hitcontext['hit_message'] = hit_count_response.hit_message
        hitcontext['total_hits'] = hits

    comments = news.comments.filter(active=True)
    comment_count = comments.count()
    new_comment = None
    if request.method == "POST":
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.news = news
            new_comment.user = request.user

            new_comment.save()

            comment_form = CommentForm()
    else:
        comment_form = CommentForm()
    context = {
        'news': news,
        'comments': comments,
        'comment_count': comment_count,
        'news_comment': new_comment,
        'comment_form': comment_form
    }

    return render(request, 'news/news_detail.html', context)


def homePageView(request):
    news_list = News.published.all().order_by('-publish_time')[:5]
    categories = Category.objects.all()
    mahalliy_one = News.published.all().filter(category__name="Mahalliy").order_by("-publish_time")[0]
    mahalliy_news = News.published.all().filter(category__name="Mahalliy").order_by("-publish_time")[1:5]
    context = {
        'news_list': news_list,
        'categories': categories,
        'mahalliy_one': mahalliy_one,
        'mahalliy_news': mahalliy_news
    }

    return render(request, 'news/index.html', context)

class HomePageView(ListView):
    model = News
    template_name = 'news/index.html'
    context_object_name = 'news'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['news_list'] = News.published.all().order_by('-publish_time')[:5]
        context['mahalliy_one'] = News.published.all().filter(category__name="Mahalliy").order_by("-publish_time")[0]
        context['mahalliy_news'] = News.published.all().filter(category__name="Mahalliy").order_by("-publish_time")[1:5]

        context['xorij_one'] = News.published.all().filter(category__name="Xorijiy").order_by("-publish_time")[0]
        context['xorij_news'] = News.published.all().filter(category__name="Xorijiy").order_by("-publish_time")[1:5]

        context['sport_one'] = News.published.all().filter(category__name="Sport").order_by("-publish_time")[0]
        context['sport_news'] = News.published.all().filter(category__name="Sport").order_by("-publish_time")[1:5]

        context['texnologiya_one'] = News.published.all().filter(category__name="Texnologiya").order_by("-publish_time")[0]
        context['texnologiya_news'] = News.published.all().filter(category__name="Texnologiya").order_by("-publish_time")[1:5]

        return context

# def conatactPageView(request):
#     form = ContactForm(request.POST or None)
#     if request.method == "POST" and form.is_valid():
#         form.save()
#         return HttpResponse("<h2> Biz bilan bog'langaningiz uchun rahmat </h2>")
    
#     context = {
#         "form": form
#     }

#     return render(request, 'news/contact.html', context)

class ContactPageView(TemplateView):
    template_name = 'news/contact.html'

    def get(self, request, *args, **kwargs):
        form = ContactForm()
        context = {
            "form": form
        }
        return render(request, 'news/contact.html', context)
    
    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if request.method == "POST" and form.is_valid():
            form.save()
            return HttpResponse("<h2> Biz bilan bog'langaningiz uchun rahmat </h2>")
        
        context = {
            "form": form
        }
        return render(request, 'news/contact.html', context)


class LocalNewsView(ListView):
    model = News
    template_name = 'news/mahalliy.html'
    context_object_name = 'mahalliy_yangiliklar'

    def get_queryset(self):
        news = self.model.published.all().filter(category__name="Mahalliy")
        return news


class ForeignNewsView(ListView):
    model = News
    template_name = 'news/xorij.html'
    context_object_name = 'xorijiy_yangiliklar'

    def get_queryset(self):
        news = self.model.published.all().filter(category__name="Xorijiy")
        return news

class TechnologyNewsView(ListView):
    model = News
    template_name = 'news/texnologiya.html'
    context_object_name = 'texnologiya_yangiliklar'

    def get_queryset(self):
        news = self.model.published.all().filter(category__name="Texnologiya")
        return news

class SportNewsView(ListView):
    model = News
    template_name = 'news/sport.html'
    context_object_name = 'sport_yangiliklar'

    def get_queryset(self):
        news = self.model.published.all().filter(category__name="Sport")
        return news

class NewsUpdateView(OnlyLoggedSuperUser, UpdateView):
    model = News
    fields = ('title', 'body', 'image', 'category', 'status',)
    template_name = 'crud/news_edit.html'

class NewsDeleteView(OnlyLoggedSuperUser, DeleteView):
    model = News
    template_name = 'crud/news_delete.html'
    success_url = reverse_lazy('home_page')

class NewsCreateView(OnlyLoggedSuperUser, CreateView):
    model = News
    template_name = 'crud/news_create.html'
    fields = ('title', 'slug', 'body', 'image', 'category', 'status')

@login_required
@user_passes_test(lambda u:u.is_superuser)
def admin_page_view(request):
    admin_users = User.objects.filter(is_superuser=True)

    context = {
        'admin_users': admin_users
    }

    return render(request, 'pages/admin_page.html', context)

class SearchResultList(ListView):
    model = News
    template_name = 'news/search_result.html'
    context_object_name = 'barcha_yangiliklar'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return News.objects.filter(
                Q(title__icontains=query) | Q(body__icontains=query)
            )