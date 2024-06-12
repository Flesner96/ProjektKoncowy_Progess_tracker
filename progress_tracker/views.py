from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.forms import modelformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView, DetailView, DeleteView
from .models import Game, Quest, CharacterQuestProgress, Character, Comment, QuestStep, CharacterQuestStepProgress
from .forms import GameForm, QuestForm, CharacterForm, QuestStepForm, CommentForm, CharacterQuestProgressForm, \
 CharacterQuestStepProgressForm
from .utils import is_superuser


# Create your views here.

@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    def get(self, request):
        return render(request, 'dashboard.html')

    def post(self, request):
        if request.user.is_authenticated:
            context = {
                'user': request.user,
                'example_data': 'Przykładowe dane do przekazania do szablonu'
            }
            return render(request, 'dashboard.html', context)
        else:
            return HttpResponse("User is not authenticated")


@method_decorator(user_passes_test(is_superuser), name='dispatch')
class CreateGameView(CreateView):
    model = Game
    form_class = GameForm
    template_name = 'progres_tracker/add_game.html'
    success_url = reverse_lazy('game_list')


@method_decorator(user_passes_test(is_superuser), name='dispatch')
class UpdateGameView(UpdateView):
    model = Game
    form_class = GameForm
    template_name = 'progres_tracker/edit_game.html'
    success_url = reverse_lazy('game_list')


@method_decorator(user_passes_test(is_superuser), name='dispatch')
class CreateQuestView(CreateView):
    model = Quest
    form_class = QuestForm
    template_name = 'progres_tracker/add_quest.html'
    success_url = reverse_lazy('quest_list')


@method_decorator(user_passes_test(is_superuser), name='dispatch')
class UpdateQuestView(UpdateView):
    model = Quest
    form_class = QuestForm
    template_name = 'progres_tracker/edit_quest.html'
    success_url = reverse_lazy('quest_list')


class CreateCharacterView(LoginRequiredMixin, CreateView):
    login_url = '/login/'
    form_class = CharacterForm
    template_name = 'progres_tracker/add_character.html'
    success_url = reverse_lazy('character_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class UpdateCharacterView(UpdateView):
    model = Character
    form_class = CharacterForm
    template_name = 'progres_tracker/edit_character.html'
    success_url = reverse_lazy('character_list')


@login_required
def character_delete(request, id):
    char_to_delete = get_object_or_404(Character, id=id)

    if char_to_delete.user != request.user:
        context = {'error': "You do not have permission to delete this character."}
        return render(request, 'progres_tracker/character_detail.html', context)

    if request.method == 'POST':
        char_to_delete.delete()
        return HttpResponseRedirect(reverse('character_list'))

    return render(request, 'progres_tracker/character_delete_confirm.html', {'char': char_to_delete})


@method_decorator(login_required, name='dispatch')
class QuestListView(ListView):
    model = Quest
    template_name = 'progres_tracker/quest_list.html'
    context_object_name = 'quest_list'


@method_decorator(login_required, name='dispatch')
class QuestDetailView(DetailView):
    model = Quest
    template_name = 'progres_tracker/quest_detail.html'
    context_object_name = 'quest'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(quest=self.object)
        context['quest_steps'] = QuestStep.objects.filter(quest=self.object)
        return context


@method_decorator(user_passes_test(is_superuser), name='dispatch')
class QuestDeleteView(DeleteView):
    model = Quest
    template_name = 'progres_tracker/quest_confirm_delete.html'
    success_url = reverse_lazy('quest_list')


class GameListView(ListView):
    model = Game
    template_name = 'progres_tracker/game_list.html'
    context_object_name = 'games'


class GameDetailView(DetailView):
    model = Game
    template_name = 'progres_tracker/game_detail.html'
    context_object_name = 'game'


@method_decorator(user_passes_test(is_superuser), name='dispatch')
class GameDeleteView(DeleteView):
    model = Game
    template_name = 'progres_tracker/game_confirm_delete.html'
    success_url = reverse_lazy('game_list')


def CharacterListView(request):
    characters = Character.objects.all()
    return render(request, 'progres_tracker/character_list.html', {'characters': characters})


class CharacterDetailView(View):
    def get(self, request, *args, **kwargs):
        character = Character.objects.get(pk=kwargs['id'])
        return render(request, 'progres_tracker/character_detail.html', {'character': character})


@method_decorator(login_required, name='dispatch')
class CreateCommentView(CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'progres_tracker/add_comment.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.quest = get_object_or_404(Quest, id=self.kwargs['pk'])
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action_text'] = "Add Comment"
        return context

    def get_success_url(self):
        return self.object.quest.get_absolute_url()


@login_required
def search_quests(request):
    query = request.GET.get('q')
    if query:
        quests = Quest.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    else:
        quests = Quest.objects.all()
    return render(request, 'progres_tracker/search_results.html', {'quests': quests, 'query': query})


def EventsView(request):
    return render(request, 'Giveria/events.html')


def BossesView(request):
    return render(request, 'Giveria/bosses.html')


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    fields = ['content']
    template_name = 'progres_tracker/add_comment.html'

    def form_valid(self, form):
        return super().form_valid(form)

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.user

    def get_success_url(self):
        return reverse('quest-detail', kwargs={'pk': self.object.quest.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action_text'] = "Edit Comment"
        return context


@method_decorator(user_passes_test(is_superuser), name='dispatch')
class CreateQuestStepView(CreateView):
    model = QuestStep
    form_class = QuestStepForm
    template_name = 'progres_tracker/add_quest_step.html'
    success_url = reverse_lazy('add_quest_step')


@method_decorator(login_required, name='dispatch')
class CharacterQuestProgressCreateView(CreateView):
    model = CharacterQuestProgress
    form_class = CharacterQuestProgressForm
    template_name = 'progres_tracker/characterquestprogress_form.html'
    success_url = reverse_lazy('quest_list')


@method_decorator(login_required, name='dispatch')
class CharacterQuestProgressUpdateView(UpdateView):
    model = CharacterQuestProgress
    form_class = CharacterQuestProgressForm
    template_name = 'progres_tracker/characterquestprogress_form.html'
    success_url = reverse_lazy('quest_list')



@method_decorator(login_required, name='dispatch')
class CharacterQuestStepProgressCreateView(CreateView):
    model = CharacterQuestStepProgress
    form_class = CharacterQuestStepProgressForm
    template_name = 'progres_tracker/characterqueststepprogress_form.html'
    success_url = reverse_lazy('dashboard')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        character_id = self.kwargs.get('character_id')
        character = get_object_or_404(Character, id=character_id)
        kwargs['initial']['character'] = character
        return kwargs

    def form_valid(self, form):
        character_id = self.kwargs.get('character_id')
        character = get_object_or_404(Character, id=character_id)
        form.instance.character = character
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class CharacterQuestProgressManageView(View):
    def get(self, request, character_id):
        character = get_object_or_404(Character, pk=character_id)
        quests = Quest.objects.filter(game=character.game).distinct()

        # Initialize progress_dict to keep track of completion status
        progress_dict = {}
        for quest in quests:
            for step in quest.queststep_set.all():
                progress = CharacterQuestStepProgress.objects.filter(character=character, quest_step=step).first()
                progress_dict[step.id] = progress.completed if progress else False

        return render(request, 'progres_tracker/character_progress_manage.html', {
            'character': character,
            'quests': quests,
            'progress_dict': progress_dict
        })

    def post(self, request, character_id):
        character = get_object_or_404(Character, pk=character_id)
        quest_steps = QuestStep.objects.filter(quest__game=character.game)

        # Update progress based on POST data
        for step in quest_steps:
            completed = request.POST.get(f'completed_{step.id}', 'off') == 'on'
            progress, created = CharacterQuestStepProgress.objects.get_or_create(character=character, quest_step=step)
            progress.completed = completed
            progress.save()

        return redirect('character-progress-manage', character_id=character.id)