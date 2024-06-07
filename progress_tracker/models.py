from django.db import models
from django.contrib.auth.models import User


class Game(models.Model):
    """
    Game Class

    A class representing a game.

    Attributes:
        name (str): The name of the game.

    Methods:
        __str__(): Returns the name of the game.

    """
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Quest(models.Model):
    """
    Quest

    A class representing a quest.

    Attributes:
        name (str): The name of the quest (max 200 characters).
        description (str): The description of the quest.
        steps (list): The list of steps for the quest (default is an empty list).

    Methods:
        __str__(): Returns a string representation of the quest.

    """
    name = models.CharField(max_length=200)
    description = models.TextField()
    steps = models.JSONField(default=list)

    def __str__(self):
        return self.name


class Character(models.Model):
    """
    Represents a character in a game.

    :param name: The name of the character.
    :type name: str
    :param profession: The profession of the character.
    :type profession: str
    :param game: The game the character belongs to.
    :type game: Game
    :param user: The user who owns the character.
    :type user: User
    :param quests: The quests the character has progressed through.
    :type quests: ManyToManyField(Quest)
    """
    name = models.CharField(max_length=100)
    profession = models.CharField(max_length=100)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quests = models.ManyToManyField(Quest, through='CharacterQuestProgress')

    def __str__(self):
        return self.name


class CharacterQuestProgress(models.Model):
    """

    CharacterQuestProgress

    This class represents the progress of a character in a specific quest.

    Attributes:
        - character (models.ForeignKey): The foreign key to the Character model indicating which character this progress belongs to.
        - quest (models.ForeignKey): The foreign key to the Quest model indicating which quest this progress is for.
        - progress (models.JSONField): A JSONField to store the progress of the character in the quest. This field defaults to an empty list.
        - completed (models.BooleanField): A boolean field indicating whether the quest has been completed by the character. This field defaults to False.

    Meta:
        - unique_together (list): Specifies that the combination of the character and quest fields should be unique,
        ensuring that each character can only have one progress object for a particular quest.

    """
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    progress = models.JSONField(default=list)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ['character', 'quest']


class Comment(models.Model):
    """Represents a comment made by a user on a quest.

    Attributes:
        user (ForeignKey): The user who made the comment.
        quest (ForeignKey): The quest on which the comment is made.
        content (TextField): The content of the comment.
        created_at (DateTimeField): The date and time when the comment was created.

    Methods:
        __str__: Returns a string representation of the comment.

    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quest.name}"
