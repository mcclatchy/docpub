from django.forms import ModelForm, PasswordInput, CharField
from docs.models import DocumentCloudCredentials


class PasswordInline(ModelForm):
    # password = CharField(widget=PasswordInput)

    class Meta:
        # password = forms.CharField(widget=forms.PasswordInput)
        model = DocumentCloudCredentials
        # fields = "__all__" 
        fields = ('password',)
        widgets = {
            'password': PasswordInput(render_value=True),
        }