from django import forms
from .models import Business, Comment, Rating, Category, Tag


class BusinessForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Business
        fields = [
            'name',
            'description',
            'location',
            'latitude',
            'longitude',
            'image',
            'category',
            'tags',
        ]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


class RatingForm(forms.ModelForm):
    stars = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect,
        label="Rating"
    )

    class Meta:
        model = Rating
        fields = ['stars']
