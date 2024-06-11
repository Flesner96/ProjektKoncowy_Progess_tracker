from django.urls import path

from progress_tracker import views
from progress_tracker.views import DashboardView, search_quests, GameListView, GameDetailView, CreateGameView, \
    UpdateGameView, GameDeleteView, CharacterQuestProgressUpdateView, CharacterQuestProgressCreateView, QuestListView, \
    QuestDeleteView, UpdateQuestView, CreateQuestView, CreateCharacterView, CreateCommentView, QuestDetailView, \
    CharacterListView, CharacterDetailView, CreateQuestStepView

urlpatterns = [

    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('character/new/', CreateCharacterView.as_view(), name='character_create'),
    path('quests/<int:pk>/', QuestDetailView.as_view(), name='quest_detail'),
    path('quests/add/', CreateQuestView.as_view(), name='add_quest'),
    path('quests/edit/<int:pk>/', UpdateQuestView.as_view(), name='edit_quest'),
    path('quests/delete/<int:pk>/', QuestDeleteView.as_view(), name='delete_quest'),
    path('quests/', QuestListView.as_view(), name='quest_list'),
    path('characterquestprogress/add/', CharacterQuestProgressCreateView.as_view(), name='add_characterquestprogress'),
    path('characterquestprogress/edit/<int:pk>/', CharacterQuestProgressUpdateView.as_view(),
         name='edit_characterquestprogress'),
    path('character_detail/<int:id>/', CharacterDetailView.as_view(), name='character_detail'),
    path('quests/<int:pk>/comment/', CreateCommentView.as_view(), name='comment_create'),
    path('search/', search_quests, name='search_quests'),
    path('games/', GameListView.as_view(), name='game_list'),
    path('games/<int:pk>/', GameDetailView.as_view(), name='game_detail'),
    path('games/add/', CreateGameView.as_view(), name='add_game'),
    path('games/edit/<int:pk>/', UpdateGameView.as_view(), name='edit_game'),
    path('games/delete/<int:pk>/', GameDeleteView.as_view(), name='delete_game'),
    path('character_list/', CharacterListView, name='character_list'),
    path('character_delete/<int:id>/', views.character_delete, name="character_delete"),
    path('events/', views.EventsView, name='events'),
    path('bosses/', views.BossesView, name='bosses'),
    path('add_step/', CreateQuestStepView.as_view(), name='add_quest_step'),
]
