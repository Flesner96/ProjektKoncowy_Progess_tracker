from django.db import models
from django.contrib.auth.models import User

class Game(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Quest(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Character(models.Model):
    name = models.CharField(max_length=100)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quests = models.ManyToManyField(Quest, through='CharacterQuestProgress')

    def __str__(self):
        return self.name

class QuestStep(models.Model):
    description = models.TextField()
    name = models.CharField(max_length=100)
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    order = models.IntegerField()

    def __str__(self):
        return self.name

class CharacterQuestProgress(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)  # Track overall quest completion

    class Meta:
        unique_together = ['character', 'quest']

class CharacterQuestStepProgress(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    quest_step = models.ForeignKey(QuestStep, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ['character', 'quest_step']

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quest.name}"
