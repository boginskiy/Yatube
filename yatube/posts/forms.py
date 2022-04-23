from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        labels = {
            'text': 'Введите сообщение',
            'group': 'Выберите группу',
            'image': 'Добавить изображение',
        }
        fields = ('text', 'group', 'image')
        help_text = {
            'text': 'Пост должен содержать историю известного человека',
            'group': 'Выбрать среди доступных или без группы',
            'image': 'Тематическое изображение для визуализации поста'
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
