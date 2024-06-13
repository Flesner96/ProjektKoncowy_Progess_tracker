from django import forms

from .models import Game, Quest, Character, QuestStep, Comment, CharacterQuestProgress, CharacterQuestStepProgress


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['name']


class QuestForm(forms.ModelForm):
    class Meta:
        model = Quest
        fields = ['name', 'description', 'game']


class CharacterForm(forms.ModelForm):
    class Meta:
        model = Character
        fields = ['name', 'game']


class QuestStepForm(forms.ModelForm):
    class Meta:
        model = QuestStep
        fields = ['name', 'description', 'quest', 'order']


class CharacterQuestProgressForm(forms.ModelForm):
    class Meta:
        model = CharacterQuestProgress
        fields = ['character', 'quest', 'completed']

    def __init__(self, *args, **kwargs):
        super(CharacterQuestProgressForm, self).__init__(*args, **kwargs)
        self.fields['character'].queryset = Character.objects.all()

class CharacterQuestStepProgressForm(forms.ModelForm):
    class Meta:
        model = CharacterQuestStepProgress
        fields = ['character', 'quest_step', 'completed']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['character'].widget = forms.HiddenInput()
        self.fields['quest_step'].widget = forms.HiddenInput()


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Add a comment...'}),
        }