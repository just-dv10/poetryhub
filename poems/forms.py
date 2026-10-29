from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser, Poem, Comment, GENRE_CHOICES, ChatGroup, GroupMessage, DirectMessage



class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        min_length=8,
        label='Password'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
        label='Confirm Password'
    )

    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'password']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        pw = cleaned_data.get('password')
        cpw = cleaned_data.get('confirm_password')
        if pw and cpw and pw != cpw:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )


class PoemForm(forms.ModelForm):
    class Meta:
        model = Poem
        fields = ['title', 'content', 'genre']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Poem Title'}),
            'content': forms.Textarea(attrs={
                'class': 'form-control poem-textarea',
                'placeholder': 'Write your poem here...',
                'rows': 12
            }),
            'genre': forms.Select(attrs={'class': 'form-select'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your thoughts...',
                'rows': 3
            })
        }
        labels = {'text': ''}


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['name', 'bio', 'avatar']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell us about yourself...'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }


class DirectMessageForm(forms.ModelForm):
    class Meta:
        model = DirectMessage
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'form-control chat-input',
                'placeholder': 'Type a message...',
                'autocomplete': 'off',
            })
        }
        labels = {'content': ''}


class GroupCreateForm(forms.ModelForm):
    class Meta:
        model = ChatGroup
        fields = ['name', 'description', 'avatar']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Group name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'What is this group about?'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }


class GroupMessageForm(forms.ModelForm):
    class Meta:
        model = GroupMessage
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'form-control chat-input',
                'placeholder': 'Type a message...',
                'autocomplete': 'off',
            })
        }
        labels = {'content': ''}

