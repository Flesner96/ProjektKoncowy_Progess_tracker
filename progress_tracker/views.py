from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView, DetailView, DeleteView
from .models import Game, Quest, CharacterQuestProgress, Character, Comment, QuestStep
from .forms import GameForm, QuestForm, CharacterForm, QuestStepForm, CommentForm, CharacterQuestProgressForm
from .utils import is_superuser

# Create your views here.



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
    success_url = '/games/'


@method_decorator(user_passes_test(is_superuser), name='dispatch')
class UpdateGameView(UpdateView):
    model = Game
    form_class = GameForm
    template_name = 'progres_tracker/edit_game.html'
    success_url = '/games/'


@method_decorator(user_passes_test(is_superuser), name='dispatch')
class CreateQuestView(CreateView):
    model = Quest
    form_class = QuestForm
    template_name = 'progres_tracker/add_quest.html'
    success_url = '/quests/'


@method_decorator(user_passes_test(is_superuser), name='dispatch')
class UpdateQuestView(UpdateView):
    model = Quest
    form_class = QuestForm
    template_name = 'progres_tracker/edit_quest.html'
    success_url = '/quests/'


@method_decorator(login_required, name='dispatch')
class CreateCharacterView(CreateView):
    model = Character
    form_class = CharacterForm
    template_name = 'progres_tracker/add_character.html'
    success_url = '/characters/'


@method_decorator(login_required, name='dispatch')
class UpdateCharacterView(UpdateView):
    model = Character
    form_class = CharacterForm
    template_name = 'progres_tracker/edit_character.html'
    success_url = '/characters/'


@method_decorator(login_required, name='dispatch')
class QuestListView(ListView):
    model = Quest
    template_name = 'progres_tracker/quest_list.html'
    context_object_name = 'quests'


@method_decorator(login_required, name='dispatch')
class QuestDetailView(DetailView):
    model = Quest
    template_name = 'progres_tracker/quest_detail.html'
    context_object_name = 'quest'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(quest=self.object)
        return context


@method_decorator(user_passes_test(is_superuser), name='dispatch')
class QuestDeleteView(DeleteView):
    model = Quest
    template_name = 'progres_tracker/quest_confirm_delete.html'
    success_url = reverse_lazy('quest-list')


@method_decorator(login_required, name='dispatch')
class CreateQuestStepView(CreateView):
    model = QuestStep
    form_class = QuestStepForm
    template_name = 'progres_tracker/add_quest_step.html'
    success_url = '/queststeps/'


@method_decorator(login_required, name='dispatch')
class UpdateQuestStepView(UpdateView):
    model = QuestStep
    form_class = QuestStepForm
    template_name = 'progres_tracker/edit_quest_step.html'
    success_url = '/queststeps/'


@method_decorator(user_passes_test(is_superuser), name='dispatch')
class GameDeleteView(DeleteView):
    model = Game
    template_name = 'progres_tracker/game_confirm_delete.html'
    success_url = reverse_lazy('game-list')


class GameListView(ListView):
    model = Game
    template_name = 'progres_tracker/game_list.html'
    context_object_name = 'games'


class GameDetailView(DetailView):
    model = Game
    template_name = 'progres_tracker/game_detail.html'
    context_object_name = 'game'


@method_decorator(login_required, name='dispatch')
class CharacterQuestProgressCreateView(CreateView):
    model = CharacterQuestProgress
    form_class = CharacterQuestProgressForm
    template_name = 'progres_tracker/characterquestprogress_form.html'
    success_url = reverse_lazy('quest-list')


@method_decorator(login_required, name='dispatch')
class CharacterQuestProgressUpdateView(UpdateView):
    model = CharacterQuestProgress
    form_class = CharacterQuestProgressForm
    template_name = 'progres_tracker/characterquestprogress_form.html'
    success_url = reverse_lazy('quest-list')


@method_decorator(login_required, name='dispatch')
class CreateCommentView(CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'progres_tracker/add_comment.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.quest = get_object_or_404(Quest, id=self.kwargs['quest_id'])
        return super().form_valid(form)

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
