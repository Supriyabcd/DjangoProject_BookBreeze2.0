from django import forms
from .models import UserProfile, Genre, BookList, Shelf, Book

class PersonalDetailsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['age', 'gender', 'profession', 'languages']

class CategorySelectionForm(forms.Form):
    # Use Genre model instead of Category model for displaying genres as categories
    genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),  # Pull genres from the Genre model
        widget=forms.CheckboxSelectMultiple,  # Render checkboxes
        required=True
    )

    def clean_genres(self):
        genres = self.cleaned_data.get('genres')
        if len(genres) < 5:  # Ensure that at least 5 genres are selected
            raise forms.ValidationError('You must select at least 5 genres.')
        return genres
    
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['age', 'gender', 'profession', 'languages', 'genres']  # Customize fields as needed
        widgets = {
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'profession': forms.TextInput(attrs={'class': 'form-control'}),
            'languages': forms.TextInput(attrs={'class': 'form-control'}),
            'genres': forms.CheckboxSelectMultiple(),  # Genres as checkboxes
        }

class UpdateProgressForm(forms.ModelForm):
    pages_read = forms.IntegerField(min_value=0, label="Pages Read")
    class Meta:
        model = BookList
        fields = ['pages_read']


class ShelfForm(forms.ModelForm):
    books = forms.ModelMultipleChoiceField(
        queryset=Book.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Shelf
        fields = ['name', 'category', 'books']