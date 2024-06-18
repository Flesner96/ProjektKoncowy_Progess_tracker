import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client

from progress_tracker.models import Game, Quest, Character, Comment, QuestStep, CharacterQuestProgress, \
    CharacterQuestStepProgress


def is_superuser(user):
    return user.is_superuser


@pytest.mark.django_db
def test_dashboard_view_get_authenticated():
    user = User.objects.create_user(username='testuser', password='12345')
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.get(reverse('dashboard'))
    assert response.status_code == 200
    assert 'dashboard.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_dashboard_view_get_unauthenticated():
    client = Client()
    response = client.get(reverse('dashboard'))
    assert response.status_code == 302


@pytest.mark.django_db
def test_create_game_view_get():
    superuser = User.objects.create_superuser(username='admin', password='12345')
    client = Client()
    client.login(username='admin', password='12345')

    response = client.get(reverse('add_game'))
    assert response.status_code == 200
    assert 'progres_tracker/add_game.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_create_game_view_post():
    superuser = User.objects.create_superuser(username='admin', password='12345')
    client = Client()
    client.login(username='admin', password='12345')

    response = client.post(reverse('add_game'), data={
        'name': 'New Game'})
    assert response.status_code == 302
    assert Game.objects.filter(name='New Game').exists()


@pytest.mark.django_db
def test_update_game_view_get():
    superuser = User.objects.create_superuser(username='admin', password='12345')
    game = Game.objects.create(name='Old Game')
    client = Client()
    client.login(username='admin', password='12345')

    response = client.get(
        reverse('edit_game', args=[game.id]))
    assert response.status_code == 200
    assert 'progres_tracker/edit_game.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_update_game_view_post():
    superuser = User.objects.create_superuser(username='admin', password='12345')
    game = Game.objects.create(name='Old Game')
    client = Client()
    client.login(username='admin', password='12345')

    response = client.post(reverse('edit_game', args=[game.id]), data={
        'name': 'Updated Game'})
    assert response.status_code == 302
    game.refresh_from_db()
    assert game.name == 'Updated Game'


@pytest.mark.django_db
def test_create_quest_view_get_superuser():
    superuser = User.objects.create_superuser(username='admin', password='12345')
    client = Client()
    client.login(username='admin', password='12345')

    response = client.get(reverse('add_quest'))
    assert response.status_code == 200
    assert 'progres_tracker/add_quest.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_create_quest_view_post_missing_fields():
    superuser = User.objects.create_superuser(username='admin', password='12345')
    client = Client()
    client.login(username='admin', password='12345')

    response = client.post(reverse('add_quest'), data={})
    print(f"Superuser POST with Missing Fields Response status code: {response.status_code}")
    assert response.status_code == 200
    assert 'This field is required.' in response.content.decode()
    assert not Quest.objects.exists()


@pytest.mark.django_db
def test_update_quest_view_post_authenticated_non_superuser():
    user = User.objects.create_user(username='testuser', password='12345')
    game = Game.objects.create(name='Test Game')
    quest = Quest.objects.create(name='Test Quest', game=game)
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.post(reverse('edit_quest', kwargs={'pk': quest.pk}),
                           data={'name': 'Updated Quest', 'game': game.pk}, follow=True)

    assert response.redirect_chain[-1][1] == 302

    assert response.redirect_chain[-1][0].startswith('/accounts/login/')

    quest.refresh_from_db()
    assert quest.name == 'Test Quest'


@pytest.mark.django_db
def test_update_quest_view_post_unauthenticated_user():
    game = Game.objects.create(name='Test Game')
    quest = Quest.objects.create(name='Test Quest', game=game)
    client = Client()

    response = client.post(reverse('edit_quest', kwargs={'pk': quest.pk}),
                           data={'name': 'Updated Quest', 'game': game.pk}, follow=True)

    assert response.redirect_chain[-1][1] == 302
    assert response.redirect_chain[-1][0].startswith('/accounts/login/')

    quest.refresh_from_db()
    assert quest.name == 'Test Quest'


@pytest.mark.django_db
def test_create_character_view_get_regular_user():
    user = User.objects.create_user(username='testuser1', password='12345')
    client = Client()
    client.login(username='testuser1', password='12345')

    response = client.get(reverse('character_create'))
    assert response.status_code == 200
    assert 'progres_tracker/add_character.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_create_character_view_post_invalid_data():
    user = User.objects.create_user(username='testuser1', password='12345')
    client = Client()
    client.login(username='testuser1', password='12345')

    response = client.post(reverse('character_create'), data={'name': ''})
    assert response.status_code == 200  #
    assert not Character.objects.exists()
    assert 'This field is required.' in response.content.decode()


@pytest.mark.django_db
def test_character_delete_view_get_authorized_user():
    user = User.objects.create_user(username='testuser', password='12345')
    game = Game.objects.create(name='Test Game')
    character = Character.objects.create(name='Test Character', user=user, game=game)
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.get(
        reverse('character_delete', args=[character.id]))
    assert response.status_code == 200
    assert 'progres_tracker/character_delete_confirm.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_character_delete_view_post_unauthorized_user():
    owner = User.objects.create_user(username='owner', password='12345')
    other_user = User.objects.create_user(username='otheruser', password='12345')
    game = Game.objects.create(name='Test Game')
    character = Character.objects.create(name='Test Character', user=owner, game=game)
    client = Client()
    client.login(username='otheruser', password='12345')

    response = client.post(reverse('character_delete', args=[character.id]))
    assert response.status_code == 403  # Forbidden
    assert Character.objects.filter(id=character.id).exists()


@pytest.mark.django_db
def test_quest_list_view_authenticated_user():
    user = User.objects.create_user(username='testuser', password='12345')
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.get(reverse('quest_list'))
    assert response.status_code == 200
    assert 'progres_tracker/quest_list.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_quest_list_view_multiple_quests():
    client = Client()
    game = Game.objects.create(name='Test Game')
    Quest.objects.create(name='Quest 1', game=game)
    Quest.objects.create(name='Quest 2', game=game)
    Quest.objects.create(name='Quest 3', game=game)

    response = client.get(reverse('quest_list'))  # Ensure 'quest_list' is the correct URL pattern name
    assert response.status_code == 200
    assert 'progres_tracker/quest_list.html' in [t.name for t in response.templates]
    assert 'quests' in response.context
    assert len(response.context['quests']) == 3  # Ensure the quests context variable contains all the created quests
    quest_names = [quest.name for quest in response.context['quests']]
    assert 'Quest 1' in quest_names
    assert 'Quest 2' in quest_names
    assert 'Quest 3' in quest_names


@pytest.mark.django_db
def test_quest_detail_view_get_authenticated_user():
    user = User.objects.create_user(username='testuser', password='12345')
    game = Game.objects.create(name='Test Game')
    quest = Quest.objects.create(name='Test Quest', game=game)
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.get(reverse('quest_detail', args=[quest.pk]))
    assert response.status_code == 200
    assert 'progres_tracker/quest_detail.html' in [t.name for t in response.templates]
    assert 'quest' in response.context
    assert 'quest_steps' in response.context
    assert 'comments' in response.context
    assert 'comment_form' in response.context


@pytest.mark.django_db
def test_quest_detail_view_post_authenticated_user_valid_data():
    user = User.objects.create_user(username='testuser', password='12345')
    game = Game.objects.create(name='Test Game')
    quest = Quest.objects.create(name='Test Quest', game=game)
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.post(reverse('quest_detail', args=[quest.pk]), data={'content': 'Test Comment'})
    assert response.status_code == 302
    assert Comment.objects.filter(content='Test Comment', quest=quest, user=user).exists()


@pytest.mark.django_db
def test_quest_delete_view_get_superuser():
    superuser = User.objects.create_superuser(username='admin', password='12345')
    game = Game.objects.create(name='Test Game')
    quest = Quest.objects.create(name='Test Quest', game=game)
    client = Client()
    client.login(username='admin', password='12345')

    response = client.get(reverse('delete_quest', args=[quest.pk]))
    assert response.status_code == 200
    assert 'progres_tracker/quest_confirm_delete.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_quest_delete_view_post_anonymous_user():
    superuser = User.objects.create_superuser(username='admin', password='12345')
    game = Game.objects.create(name='Test Game')
    quest = Quest.objects.create(name='Test Quest', game=game)
    client = Client()

    response = client.post(reverse('delete_quest', args=[quest.pk]))
    assert response.status_code == 302
    assert 'login' in response.url
    assert Quest.objects.filter(id=quest.id).exists()


@pytest.mark.django_db
def test_game_list_view_get_authenticated_user():
    user = User.objects.create_user(username='testuser', password='12345')
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.get(reverse('game_list'))
    assert response.status_code == 200
    assert 'progres_tracker/game_list.html' in [t.name for t in response.templates]
    assert 'games' in response.context


@pytest.mark.django_db
def test_game_list_view_no_games():
    user = User.objects.create_user(username='testuser', password='12345')
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.get(reverse('game_list'))
    assert response.status_code == 200
    assert 'progres_tracker/game_list.html' in [t.name for t in response.templates]
    assert 'games' in response.context
    assert len(response.context['games']) == 0


@pytest.mark.django_db
def test_game_detail_view_get_authenticated_user():
    user = User.objects.create_user(username='testuser', password='12345')
    game = Game.objects.create(name='Test Game')
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.get(
        reverse('game_detail', args=[game.pk]))
    assert response.status_code == 200
    assert 'progres_tracker/game_detail.html' in [t.name for t in response.templates]
    assert 'game' in response.context
    assert response.context['game'] == game


@pytest.mark.django_db
def test_game_detail_view_get_non_existent_game():
    user = User.objects.create_user(username='testuser', password='12345')
    client = Client()
    client.login(username='testuser', password='12345')

    non_existent_game_id = 9999

    response = client.get(
        reverse('game_detail', args=[non_existent_game_id]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_game_delete_view_post_superuser():
    superuser = User.objects.create_superuser(username='admin', password='12345')
    game = Game.objects.create(name='Test Game')
    client = Client()
    client.login(username='admin', password='12345')

    response = client.post(reverse('delete_game', args=[game.pk]))
    assert response.status_code == 302
    assert not Game.objects.filter(id=game.id).exists()


@pytest.mark.django_db
def test_game_delete_view_post_anonymous_user():
    game = Game.objects.create(name='Test Game')
    client = Client()

    response = client.post(reverse('delete_game', args=[game.pk]))
    assert response.status_code == 302
    assert 'login' in response.url
    assert Game.objects.filter(id=game.id).exists()


@pytest.mark.django_db
def test_character_list_view_get_authenticated_user():
    user = User.objects.create_user(username='testuser', password='12345')
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.get(reverse('character_list'))
    assert response.status_code == 200
    assert 'progres_tracker/character_list.html' in [t.name for t in response.templates]
    assert 'characters' in response.context


@pytest.mark.django_db
def test_character_list_view_no_characters():
    user = User.objects.create_user(username='testuser', password='12345')
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.get(reverse('character_list'))
    assert response.status_code == 200
    assert 'progres_tracker/character_list.html' in [t.name for t in response.templates]
    assert 'characters' in response.context
    assert len(response.context['characters']) == 0


@pytest.mark.django_db
def test_character_detail_view_get_non_existent_character():
    user = User.objects.create_user(username='testuser', password='12345')
    client = Client()
    client.login(username='testuser', password='12345')

    non_existent_character_id = 9999

    response = client.get(reverse('character_detail', kwargs={
        'id': non_existent_character_id}))
    assert response.status_code == 404


@pytest.mark.django_db
def test_character_detail_view_get_authenticated_user_other_character():
    user1 = User.objects.create_user(username='testuser1', password='12345')
    user2 = User.objects.create_user(username='testuser2', password='12345')
    game = Game.objects.create(name='Test Game')
    character = Character.objects.create(name='Test Character', user=user1, game=game)
    client = Client()
    client.login(username='testuser2', password='12345')

    response = client.get(reverse('character_detail', kwargs={
        'id': character.pk}))
    assert response.status_code == 200
    assert 'progres_tracker/character_detail.html' in [t.name for t in response.templates]
    assert 'character' in response.context
    assert response.context['character'] == character
    assert response.context['is_owner'] is False


@pytest.mark.django_db
def test_create_comment_view_get_authenticated_user():
    user = User.objects.create_user(username='testuser', password='12345')
    game = Game.objects.create(name='Test Game')
    quest = Quest.objects.create(name='Test Quest', game=game)
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.get(
        reverse('comment_create', kwargs={'pk': quest.pk}))
    assert response.status_code == 200
    assert 'progres_tracker/add_comment.html' in [t.name for t in response.templates]
    assert 'form' in response.context


@pytest.mark.django_db
def test_create_comment_view_post_unauthenticated_user():
    game = Game.objects.create(name='Test Game')
    quest = Quest.objects.create(name='Test Quest', game=game)
    client = Client()

    response = client.post(reverse('comment_create', kwargs={'pk': quest.pk}), data={'content': 'Test Comment'})
    assert response.status_code == 302
    assert 'login' in response.url
    assert not Comment.objects.filter(content='Test Comment', quest=quest).exists()


@pytest.mark.django_db
def test_events_view_get_authenticated_user():
    user = User.objects.create_user(username='testuser', password='12345')
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.get(reverse('events'))
    assert response.status_code == 200
    assert 'Giveria/events.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_bosses_view_get_authenticated_user():
    user = User.objects.create_user(username='testuser', password='12345')
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.get(reverse('bosses'))
    assert response.status_code == 200
    assert 'Giveria/bosses.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_create_quest_step_view_get_superuser():
    superuser = User.objects.create_superuser(username='admin', password='12345')
    game = Game.objects.create(name='Test Game')
    quest = Quest.objects.create(name='Test Quest', game=game)
    client = Client()
    client.login(username='admin', password='12345')

    response = client.get(reverse('add_quest_step'))
    assert response.status_code == 200
    assert 'progres_tracker/add_quest_step.html' in [t.name for t in response.templates]
    assert 'form' in response.context


@pytest.mark.django_db
def test_create_quest_step_view_post_superuser_invalid_data():
    superuser = User.objects.create_superuser(username='admin', password='12345')
    game = Game.objects.create(name='Test Game')
    quest = Quest.objects.create(name='Test Quest', game=game)
    client = Client()
    client.login(username='admin', password='12345')

    response = client.post(reverse('add_quest_step'),
                           data={'name': '', 'quest': quest.id, 'order': 1})
    assert response.status_code == 200
    assert not QuestStep.objects.filter(quest=quest).exists()
    assert 'This field is required.' in response.content.decode()


@pytest.mark.django_db
def test_character_quest_progress_create_view_get_authenticated_user():
    user = User.objects.create_user(username='testuser', password='12345')
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.get(reverse(
        'characterquestprogress_create'))
    assert response.status_code == 200
    assert 'progres_tracker/characterquestprogress_form.html' in [t.name for t in response.templates]
    assert 'form' in response.context


@pytest.mark.django_db
def test_character_quest_progress_create_view_post_authenticated_user_valid_data():
    user = User.objects.create_user(username='testuser', password='12345')
    game = Game.objects.create(name='Test Game')
    quest = Quest.objects.create(name='Test Quest', game=game)
    character = Character.objects.create(name='Test Character', user=user, game=game)
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.post(reverse('characterquestprogress_create'), data={
        'character': character.id,
        'quest': quest.id,
        'completed': False
    })
    assert response.status_code == 302
    assert CharacterQuestProgress.objects.filter(character=character, quest=quest).exists()


@pytest.mark.django_db
def test_character_quest_progress_update_view_get_authenticated_user():
    user = User.objects.create_user(username='testuser', password='12345')
    game = Game.objects.create(name='Test Game')
    quest = Quest.objects.create(name='Test Quest', game=game)
    character = Character.objects.create(name='Test Character', user=user, game=game)
    char_quest_progress = CharacterQuestProgress.objects.create(character=character, quest=quest, completed=False)
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.get(reverse('characterquestprogress_update', kwargs={
        'pk': char_quest_progress.pk}))
    assert response.status_code == 200
    assert 'progres_tracker/characterquestprogress_form.html' in [t.name for t in response.templates]
    assert 'form' in response.context


@pytest.mark.django_db
def test_character_quest_progress_update_view_post_authenticated_user_valid_data():
    user = User.objects.create_user(username='testuser', password='12345')
    game = Game.objects.create(name='Test Game')
    quest = Quest.objects.create(name='Test Quest', game=game)
    character = Character.objects.create(name='Test Character', user=user, game=game)
    char_quest_progress = CharacterQuestProgress.objects.create(character=character, quest=quest, completed=False)
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.post(reverse('characterquestprogress_update', kwargs={'pk': char_quest_progress.pk}), data={
        'character': character.id,
        'quest': quest.id,
        'completed': True
    })
    assert response.status_code == 302
    char_quest_progress.refresh_from_db()
    assert char_quest_progress.completed is True


@pytest.mark.django_db
def test_character_quest_step_progress_create_view_get_authenticated_user():
    user = User.objects.create_user(username='testuser', password='12345')
    game = Game.objects.create(name='Test Game')
    character = Character.objects.create(name='Test Character', user=user, game=game)
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.get(reverse('characterqueststepprogress_create', kwargs={
        'character_id': character.id}))
    assert response.status_code == 200
    assert 'progres_tracker/characterqueststepprogress_form.html' in [t.name for t in response.templates]
    assert 'form' in response.context


@pytest.mark.django_db
def test_character_quest_step_progress_create_view_post_authenticated_user_invalid_data():
    user = User.objects.create_user(username='testuser', password='12345')
    game = Game.objects.create(name='Test Game')
    quest = Quest.objects.create(name='Test Quest', game=game)
    character = Character.objects.create(name='Test Character', user=user, game=game)
    quest_step = QuestStep.objects.create(name='Test Quest Step', quest=quest, order=1)
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.post(reverse('characterqueststepprogress_create', kwargs={'character_id': character.id}), data={
        'quest_step': '',
        'completed': False
    })
    assert response.status_code == 200
    assert not CharacterQuestStepProgress.objects.filter(
        character=character).exists()
    assert 'This field is required.' in response.content.decode()


@pytest.mark.django_db
def test_character_quest_progress_manage_view_get_authenticated_user():
    user = User.objects.create_user(username='testuser', password='12345')
    game = Game.objects.create(name='Test Game')
    character = Character.objects.create(name='Test Character', user=user, game=game)
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.get(reverse('character-progress-manage', kwargs={
        'character_id': character.id}))
    assert response.status_code == 200
    assert 'progres_tracker/character_progress_manage.html' in [t.name for t in response.templates]
    assert 'character' in response.context
    assert 'quests' in response.context
    assert 'progress_dict' in response.context
    assert 'quest_completed_dict' in response.context


@pytest.mark.django_db
def test_character_quest_progress_manage_view_post_authenticated_user_valid_data():
    user = User.objects.create_user(username='testuser', password='12345')
    game = Game.objects.create(name='Test Game')
    quest = Quest.objects.create(name='Test Quest', game=game)
    character = Character.objects.create(name='Test Character', user=user, game=game)
    quest_step = QuestStep.objects.create(name='Test Quest Step', quest=quest, order=1)
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.post(reverse('character-progress-manage', kwargs={'character_id': character.id}), data={
        f'quest_completed_{quest.id}': 'on',
        f'completed_{quest_step.id}': 'on'
    })
    assert response.status_code == 302
    assert CharacterQuestProgress.objects.filter(character=character, quest=quest,
                                                 completed=True).exists()
    assert CharacterQuestStepProgress.objects.filter(character=character, quest_step=quest_step,
                                                     completed=True).exists()


@pytest.mark.django_db
def test_character_quest_progress_view_get_authenticated_user():
    user = User.objects.create_user(username='testuser', password='12345')
    game = Game.objects.create(name='Test Game')
    character = Character.objects.create(name='Test Character', user=user, game=game)
    quest = Quest.objects.create(name='Test Quest', game=game)
    quest_step = QuestStep.objects.create(name='Test Quest Step', quest=quest, order=1)
    CharacterQuestProgress.objects.create(character=character, quest=quest, completed=False)
    CharacterQuestStepProgress.objects.create(character=character, quest_step=quest_step, completed=False)
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.get(reverse('character-progress-view', kwargs={
        'character_id': character.id}))
    assert response.status_code == 200
    assert 'progres_tracker/character_progress_view.html' in [t.name for t in response.templates]
    assert 'character' in response.context
    assert 'quests' in response.context
    assert 'progress_dict' in response.context
    assert 'quest_completed_dict' in response.context


@pytest.mark.django_db
def test_character_quest_progress_view_get_unauthenticated_user():
    user = User.objects.create_user(username='testuser', password='12345')
    game = Game.objects.create(name='Test Game')
    character = Character.objects.create(name='Test Character', user=user, game=game)
    client = Client()

    response = client.get(reverse('character-progress-view', kwargs={
        'character_id': character.id}))
    assert response.status_code == 302
    assert 'login' in response.url


@pytest.mark.django_db
def test_comment_update_view_get_authenticated_user():
    user = User.objects.create_user(username='testuser', password='12345')
    game = Game.objects.create(name='Test Game')
    quest = Quest.objects.create(name='Test Quest', game=game)
    comment = Comment.objects.create(content='Original Comment', user=user, quest=quest)
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.get(
        reverse('comment_update', kwargs={'pk': comment.pk}))
    assert response.status_code == 200
    assert 'progres_tracker/comment_form.html' in [t.name for t in response.templates]
    assert 'form' in response.context
    assert 'comment' in response.context


@pytest.mark.django_db
def test_comment_update_view_post_authenticated_user_valid_data():
    user = User.objects.create_user(username='testuser', password='12345')
    game = Game.objects.create(name='Test Game')
    quest = Quest.objects.create(name='Test Quest', game=game)
    comment = Comment.objects.create(content='Original Comment', user=user, quest=quest)
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.post(reverse('comment_update', kwargs={'pk': comment.pk}), data={'content': 'Updated Comment'})
    assert response.status_code == 302
    comment.refresh_from_db()
    assert comment.content == 'Updated Comment'


@pytest.mark.django_db
def test_comment_delete_view_get_authenticated_user():
    user = User.objects.create_user(username='testuser', password='12345')
    game = Game.objects.create(name='Test Game')
    quest = Quest.objects.create(name='Test Quest', game=game)
    comment = Comment.objects.create(content='Comment to delete', user=user, quest=quest)
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.get(
        reverse('comment_delete', kwargs={'pk': comment.pk}))
    assert response.status_code == 200
    assert 'progres_tracker/comment_confirm_delete.html' in [t.name for t in response.templates]
    assert 'comment' in response.context


@pytest.mark.django_db
def test_comment_delete_view_post_unauthenticated_user():
    user = User.objects.create_user(username='testuser', password='12345')
    game = Game.objects.create(name='Test Game')
    quest = Quest.objects.create(name='Test Quest', game=game)
    comment = Comment.objects.create(content='Comment to delete', user=user, quest=quest)
    client = Client()

    response = client.post(reverse('comment_delete', kwargs={'pk': comment.pk}))
    assert response.status_code == 302
    assert 'login' in response.url
    assert Comment.objects.filter(pk=comment.pk).exists()


@pytest.mark.django_db
def test_quest_search_authenticated_user_with_query():
    user = User.objects.create_user(username='testuser', password='12345')
    game = Game.objects.create(name='Test Game')
    Quest.objects.create(name='Quest One', game=game)
    Quest.objects.create(name='Quest Two', game=game)
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.get(reverse('quest_search'), {'q': 'One'})
    assert response.status_code == 200
    assert 'Quest One' in response.json()['html']
    assert 'Quest Two' not in response.json()['html']


@pytest.mark.django_db
def test_quest_search_authenticated_user_without_query():
    user = User.objects.create_user(username='testuser', password='12345')
    game = Game.objects.create(name='Test Game')
    Quest.objects.create(name='Quest One', game=game)
    Quest.objects.create(name='Quest Two', game=game)
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.get(reverse('quest_search'))
    assert response.status_code == 200
    assert 'Quest One' in response.json()['html']
    assert 'Quest Two' in response.json()['html']


@pytest.mark.django_db
def test_character_search_with_query():
    user = User.objects.create_user(username='testuser', password='12345')
    game = Game.objects.create(name='Test Game')
    Character.objects.create(name='Character One', user=user, game=game)
    Character.objects.create(name='Character Two', user=user, game=game)
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.get(reverse('character_search'), {'q': 'One'})
    assert response.status_code == 200
    assert 'Character One' in response.json()['html']
    assert 'Character Two' not in response.json()['html']


@pytest.mark.django_db
def test_character_search_without_query():
    user = User.objects.create_user(username='testuser', password='12345')
    game = Game.objects.create(name='Test Game')
    Character.objects.create(name='Character One', user=user, game=game)
    Character.objects.create(name='Character Two', user=user, game=game)
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.get(reverse('character_search'))
    assert response.status_code == 200
    assert 'Character One' in response.json()['html']
    assert 'Character Two' in response.json()['html']


@pytest.mark.django_db
def test_quest_filter_by_game():
    user = User.objects.create_user(username='testuser', password='12345')
    game1 = Game.objects.create(name='Test Game 1')
    game2 = Game.objects.create(name='Test Game 2')
    Quest.objects.create(name='Quest One', game=game1)
    Quest.objects.create(name='Quest Two', game=game2)
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.get(reverse('quest_filter'), {'game': 'Test Game 1'})
    assert response.status_code == 200
    assert 'Quest One' in response.json()['html']
    assert 'Quest Two' not in response.json()['html']


@pytest.mark.django_db
def test_quest_filter_all():
    user = User.objects.create_user(username='testuser', password='12345')
    game1 = Game.objects.create(name='Test Game 1')
    game2 = Game.objects.create(name='Test Game 2')
    Quest.objects.create(name='Quest One', game=game1)
    Quest.objects.create(name='Quest Two', game=game2)
    client = Client()
    client.login(username='testuser', password='12345')

    response = client.get(reverse('quest_filter'), {'game': 'all'})
    assert response.status_code == 200
    assert 'Quest One' in response.json()['html']
    assert 'Quest Two' in response.json()['html']
