from django import forms
from users.models import Library, Book


class LibraryForm(forms.ModelForm):
    class Meta:
        model = Library
        fields = ['name', 'address', 'opening_time', 'closing_time']
        widgets = {
            'opening_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'closing_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
        }


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['name', 'published_on', 'author', 'libraries']
        widgets = {
            'published_on': forms.DateInput(attrs={'type': 'date'}),
            'libraries': forms.CheckboxSelectMultiple()
        }


class AddBookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['name', 'author', 'published_on']
        widgets = {
            'published_on': forms.DateInput(attrs={'type': 'date'})
        }
