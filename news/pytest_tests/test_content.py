from django.conf import settings
from datetime import datetime, timedelta

from django.urls import reverse
from django.utils import timezone
import pytest

from news.forms import CommentForm
from news.models import Comment, News


@pytest.mark.django_db
def test_home_page(client):
    HOME_URL = reverse('news:home', args=None)
    today = datetime.today()
    all_news = [
            News(
                title=f'Новость {index}',
                text='Просто текст.',
                date=today - timedelta(days=index)
            )
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        ]
    News.objects.bulk_create(all_news)
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_main_has_propper_news_order(client):
    HOME_URL = reverse('news:home', args=None)
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 2)
    ]
    News.objects.bulk_create(all_news)
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    context_dates = [news.date for news in object_list]
    sorted_dates = sorted(context_dates, reverse=True)
    assert sorted_dates == context_dates


def test_comments_order(author, author_client, newness, id_for_args):
    detail_url = reverse('news:detail', args=id_for_args)
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=newness,
            author=author,
            text=f'Tекст {index}'
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    response = author_client.get(detail_url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
@pytest.mark.parametrize('parametrized_client, expected_status',
                         ((pytest.lazy_fixture('client'), False),
                          (pytest.lazy_fixture('admin_client'), True)),)
def test_client_has_form(id_for_args, parametrized_client, expected_status):
    detail_url = reverse('news:detail', args=id_for_args)
    response = parametrized_client.get(detail_url)
    assert ('form' in response.context) == expected_status
    if 'form' in response.context:
        assert isinstance(response.context['form'], type(CommentForm()))
