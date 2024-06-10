from django import forms
from .models import Game, Quest, Character, QuestStep, Comment, CharacterQuestProgress


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
        fields = ['name', 'profession', 'game', 'user']


class QuestStepForm(forms.ModelForm):
    class Meta:
        model = QuestStep
        fields = ['name', 'description', 'quest', 'order']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']


class CharacterQuestProgressForm(forms.ModelForm):
    class Meta:
        model = CharacterQuestProgress
        fields = ['character', 'completed']
