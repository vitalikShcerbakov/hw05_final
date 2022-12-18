from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """
    Класс формы нового поста.
    """
    class Meta:
        model = Post
        labels = {
            'text': 'Текст поста',
            'group': 'Группа',
        }
        help_texts = {
            'group': 'Выберите группу',
            'text': 'Введите ссообщение'
        }
        fields = ('text', 'group')
        fields = ('group', 'text', 'image')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        labels = {
            'text': 'Текст комментария'
        }
        help_text = {
            'text': 'Введите комментария'
        }
        fields = ('text',)
