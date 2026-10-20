from django import forms
from .models import Resume

JOB_ROLES = [
    ('Python Developer', 'Python Developer'),
    ('Web Developer', 'Web Developer'),
    ('Data Analyst', 'Data Analyst'),
    ('Software Engineer', 'Software Engineer'),
]


class ResumeUploadForm(forms.ModelForm):
    job_role = forms.ChoiceField(choices=JOB_ROLES)

    class Meta:
        model = Resume
        fields = ['file']

    def clean_file(self):
        f = self.cleaned_data['file']
        if not f.name.lower().endswith('.pdf'):
            raise forms.ValidationError('Sirf PDF file upload karo.')
        if f.size > 5 * 1024 * 1024:
            raise forms.ValidationError('File 5MB se chhoti honi chahiye.')
        return f