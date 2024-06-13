from django.urls import path
from .views import (
    DashboardView, CreateCharacterView, QuestDetailView, CreateQuestView,
    UpdateQuestView, QuestDeleteView, QuestListView, CharacterDetailView,
    CreateCommentView, search_quests, GameListView, GameDetailView,
    CreateGameView, UpdateGameView, GameDeleteView, CharacterListView,
    character_delete, EventsView, BossesView, CreateQuestStepView,
    CharacterQuestStepProgressCreateView, CharacterQuestProgressManageView, CharacterQuestProgressView,
    CommentUpdateView, CommentDeleteView
)

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('character/new/', CreateCharacterView.as_view(), name='character_create'),
    path('quests/<int:pk>/', QuestDetailView.as_view(), name='quest_detail'),
    path('quests/add/', CreateQuestView.as_view(), name='add_quest'),
    path('quests/edit/<int:pk>/', UpdateQuestView.as_view(), name='edit_quest'),
    path('quests/delete/<int:pk>/', QuestDeleteView.as_view(), name='delete_quest'),
    path('quests/', QuestListView.as_view(), name='quest_list'),
    path('character_detail/<int:id>/', CharacterDetailView.as_view(), name='character_detail'),
    path('quests/<int:pk>/comment/', CreateCommentView.as_view(), name='comment_create'),
    path('search/', search_quests, name='search_quests'),
    path('games/', GameListView.as_view(), name='game_list'),
    path('games/<int:pk>/', GameDetailView.as_view(), name='game_detail'),
    path('games/add/', CreateGameView.as_view(), name='add_game'),
    path('games/edit/<int:pk>/', UpdateGameView.as_view(), name='edit_game'),
    path('games/delete/<int:pk>/', GameDeleteView.as_view(), name='delete_game'),
    path('character_list/', CharacterListView, name='character_list'),
    path('character_delete/<int:id>/', character_delete, name="character_delete"),
    path('events/', EventsView, name='events'),
    path('bosses/', BossesView, name='bosses'),
    path('add_step/', CreateQuestStepView.as_view(), name='add_quest_step'),
    path('character/<int:character_id>/progress/add/', CharacterQuestStepProgressCreateView.as_view(), name='add_character_progress'),
    path('character/<int:character_id>/progress/', CharacterQuestProgressManageView.as_view(), name='character-progress-manage'),
    path('character/<int:character_id>/view/', CharacterQuestProgressView.as_view(), name='character-progress-view'),
    path('comment/<int:pk>/edit/', CommentUpdateView.as_view(), name='comment_update'),
    path('comment/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment_delete'),
]
