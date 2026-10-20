from django import forms

SUBJECTS = [(s, s) for s in [
    'Python', 'Django', 'SQL and DBMS', 'Operating Systems',
    'Data Structures', 'Computer Networks', 'Aptitude', 'OOP Concepts',
]]
DIFFICULTY = [('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')]
COUNTS = [(5, '5 questions'), (10, '10 questions')]


class TestSelectForm(forms.Form):
    subject = forms.ChoiceField(choices=SUBJECTS)
    difficulty = forms.ChoiceField(choices=DIFFICULTY, initial='Medium')
    count = forms.TypedChoiceField(choices=COUNTS, coerce=int, initial=5)