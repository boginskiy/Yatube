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


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
