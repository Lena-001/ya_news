import pytest

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def newness():
    newness = News.objects.create(
        title='Новый заголовок',
        text='Новый текст',
    )
    return newness


@pytest.fixture
def id_for_args(newness):
    return (newness.id,)


@pytest.fixture
def comment(newness, author):
    comment = Comment.objects.create(
        news=newness,
        author=author,
        text='Новый текст',
    )
    return comment
