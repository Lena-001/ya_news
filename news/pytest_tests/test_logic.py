from django.urls import reverse
from pytest_django.asserts import assertFormError
import pytest

from news.models import Comment
from news.forms import BAD_WORDS, WARNING

NEW_COMMENT_FORM = {'text': 'Текст попытки комментировать.'}
NEW_COMMENT_TEXT = "Новый комментарий"
NEW_FORM_DATA = {'text': NEW_COMMENT_TEXT}


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(id_for_args, client, ):
    url_detail = reverse('news:detail', args=id_for_args)
    comments_count_before_request = Comment.objects.count()
    client.post(url_detail, data=NEW_COMMENT_FORM)
    comments_count_after_request = Comment.objects.count()
    assert comments_count_after_request == comments_count_before_request


@pytest.mark.django_db
def test_logged_user_can_create_comment(id_for_args, admin_client):
    url_detail = reverse('news:detail', args=id_for_args)
    comments_count_before_request = Comment.objects.count()
    admin_client.post(url_detail, data=NEW_COMMENT_FORM)
    comments_count_after_request = Comment.objects.count()
    assert comments_count_after_request == (comments_count_before_request + 1)


@pytest.mark.django_db
def test_user_cant_use_bad_words(id_for_args, admin_client):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url_detail = reverse('news:detail', args=id_for_args)
    comments_count_before_request = Comment.objects.count()
    response = admin_client.post(
        url_detail,
        data=bad_words_data
    )
    comments_count_after_request = Comment.objects.count()
    assertFormError(response, 'form', 'text', errors=(WARNING))
    assert comments_count_after_request == comments_count_before_request


@pytest.mark.django_db
def test_author_can_edit_comment(comment, author_client):
    url_edit = reverse('news:edit', args=(comment.id,))
    url_to_comments = reverse(
        'news:detail',
        args=(comment.id,)
    ) + '#comments'
    response = author_client.post(url_edit, NEW_FORM_DATA)
    comment.refresh_from_db()
    assert response.url == url_to_comments
    assert comment.text == NEW_COMMENT_TEXT


@pytest.mark.django_db
def test_alien_cant_edit_comment(comment, client):
    url_edit = reverse('news:edit', args=(comment.id,))
    url_to_comments = reverse(
        'news:detail',
        args=(comment.id,)
    ) + '#comments'
    response = client.post(url_edit, NEW_FORM_DATA)
    comment.refresh_from_db()
    assert response.url != url_to_comments
    assert comment.text != NEW_COMMENT_TEXT


@pytest.mark.django_db
def test_author_can_delete_comment(id_for_args, comment, author_client):
    url_delete = reverse('news:delete', args=(comment.id,))
    url_delete_after = reverse(
        'news:detail',
        args=id_for_args
    ) + '#comments'
    response = author_client.post(url_delete)
    assert response.url == url_delete_after


@pytest.mark.django_db
def test_alien_cant_delete_comment(id_for_args, comment, client):
    url_delete = reverse('news:delete', args=(comment.id,))
    url_delete_after = reverse(
        'news:detail',
        args=id_for_args
    ) + '#comments'
    response = client.post(url_delete)
    assert response.url != url_delete_after
