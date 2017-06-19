from django.forms import ModelForm, PasswordInput, CharField
from docs.models import DocumentCloudCredentials


class PasswordInline(ModelForm):

    class Meta:
        model = DocumentCloudCredentials
        fields = ('password',)
        widgets = {
            'password': PasswordInput(render_value=True),
        }