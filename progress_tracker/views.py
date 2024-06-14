from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, When, IntegerField
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views import View
from django.views.generic import CreateView, UpdateView, ListView, DetailView, DeleteView
from .models import Game, Quest, CharacterQuestProgress, Character, Comment, QuestStep, CharacterQuestStepProgress
from .forms import GameForm, QuestForm, CharacterForm, QuestStepForm, CommentForm, CharacterQuestProgressForm, \
    CharacterQuestStepProgressForm
from .utils import is_superuser
from django.contrib import messages


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
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


@login_required
def character_delete(request, id):
    char_to_delete = get_object_or_404(Character, id=id)

    if char_to_delete.user != request.user:
        return HttpResponseForbidden("You are not allowed to delete this character.")

    if request.method == 'POST':
        char_to_delete.delete()
        return HttpResponseRedirect(reverse('character_list'))

    return render(request, 'progres_tracker/character_delete_confirm.html', {'char': char_to_delete})

def quest_list(request):
    quests = Quest.objects.all()
    return render(request, 'progres_tracker/quest_list.html', {'quests': quests})


@method_decorator(login_required, name='dispatch')
class QuestDetailView(View):
    def get(self, request, pk):
        quest = get_object_or_404(Quest, pk=pk)
        quest_steps = QuestStep.objects.filter(quest=quest).order_by('order')
        comments = Comment.objects.filter(quest=quest).order_by('-created_at')
        comment_form = CommentForm()
        return render(request, 'progres_tracker/quest_detail.html', {
            'quest': quest,
            'quest_steps': quest_steps,
            'comments': comments,
            'comment_form': comment_form,
        })

    def post(self, request, pk):
        quest = get_object_or_404(Quest, pk=pk)
        quest_steps = QuestStep.objects.filter(quest=quest).order_by('order')
        comments = Comment.objects.filter(quest=quest).order_by('-created_at')
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.user = request.user
            new_comment.quest = quest
            new_comment.save()
            return redirect('quest_detail', pk=quest.pk)
        return render(request, 'progres_tracker/quest_detail.html', {
            'quest': quest,
            'quest_steps': quest_steps,
            'comments': comments,
            'comment_form': comment_form,
        })


@method_decorator(user_passes_test(is_superuser), name='dispatch')
class QuestDeleteView(DeleteView):
    model = Quest
    template_name = 'progres_tracker/quest_confirm_delete.html'
    success_url = reverse_lazy('quest_list')


@method_decorator(login_required, name='dispatch')
class GameListView(ListView):
    model = Game
    template_name = 'progres_tracker/game_list.html'
    context_object_name = 'games'


@method_decorator(login_required, name='dispatch')
class GameDetailView(DetailView):
    model = Game
    template_name = 'progres_tracker/game_detail.html'
    context_object_name = 'game'


@method_decorator(user_passes_test(is_superuser), name='dispatch')
class GameDeleteView(DeleteView):
    model = Game
    template_name = 'progres_tracker/game_confirm_delete.html'
    success_url = reverse_lazy('game_list')


@login_required
def CharacterListView(request):
    # Get all characters, ordering by whether the user is the owner
    characters = Character.objects.annotate(
        is_owner=Case(
            When(user=request.user, then=1),
            default=0,
            output_field=IntegerField()
        )
    ).order_by('-is_owner', 'name')
    return render(request, 'progres_tracker/character_list.html', {'characters': characters})


@method_decorator(login_required, name='dispatch')
class CharacterDetailView(View):
    def get(self, request, *args, **kwargs):
        character = get_object_or_404(Character, pk=kwargs['id'])
        is_owner = character.user == request.user
        return render(request, 'progres_tracker/character_detail.html', {
            'character': character,
            'is_owner': is_owner,
        })


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


def EventsView(request):
    return render(request, 'Giveria/events.html')


def BossesView(request):
    return render(request, 'Giveria/bosses.html')


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

        # Initialize progress_dict and quest_completed_dict
        progress_dict = {}
        quest_completed_dict = {}

        for quest in quests:
            quest_progress = CharacterQuestProgress.objects.filter(character=character, quest=quest).first()
            quest_completed_dict[quest.id] = quest_progress.completed if quest_progress else False
            for step in quest.queststep_set.all():
                progress = CharacterQuestStepProgress.objects.filter(character=character, quest_step=step).first()
                progress_dict[step.id] = progress.completed if progress else False

        return render(request, 'progres_tracker/character_progress_manage.html', {
            'character': character,
            'quests': quests,
            'progress_dict': progress_dict,
            'quest_completed_dict': quest_completed_dict,
        })

    def post(self, request, character_id):
        character = get_object_or_404(Character, pk=character_id)
        quests = Quest.objects.filter(game=character.game)

        for quest in quests:
            quest_completed = request.POST.get(f'quest_completed_{quest.id}', 'off') == 'on'
            quest_progress, created = CharacterQuestProgress.objects.get_or_create(character=character, quest=quest)
            quest_progress.completed = quest_completed
            quest_progress.save()

            steps = quest.queststep_set.all()
            step_ids = [step.id for step in steps]

            # Handle step completion
            for step_id in step_ids:
                completed = request.POST.get(f'completed_{step_id}', 'off') == 'on'
                progress, created = CharacterQuestStepProgress.objects.get_or_create(character=character,
                                                                                     quest_step_id=step_id)
                progress.completed = completed
                progress.save()

            # If the quest is marked as complete, mark all steps as complete
            if quest_completed:
                CharacterQuestStepProgress.objects.filter(character=character, quest_step__quest=quest).update(
                    completed=True)
            else:
                # If the quest has steps, check if all steps are completed
                if steps.exists():
                    all_steps_completed = CharacterQuestStepProgress.objects.filter(character=character,
                                                                                    quest_step__quest=quest,
                                                                                    completed=False).count() == 0
                    if all_steps_completed:
                        quest_progress.completed = True
                    else:
                        quest_progress.completed = False

            quest_progress.save()

        return redirect('character-progress-manage', character_id=character.id)


@method_decorator(login_required, name='dispatch')
class CharacterQuestProgressView(View):
    def get(self, request, character_id):
        character = get_object_or_404(Character, pk=character_id)
        quests = Quest.objects.filter(game=character.game).distinct()

        # Initialize progress_dict and quest_completed_dict
        progress_dict = {}
        quest_completed_dict = {}

        for quest in quests:
            quest_progress = CharacterQuestProgress.objects.filter(character=character, quest=quest).first()
            quest_completed_dict[quest.id] = quest_progress.completed if quest_progress else False
            for step in quest.queststep_set.all():
                progress = CharacterQuestStepProgress.objects.filter(character=character, quest_step=step).first()
                progress_dict[step.id] = progress.completed if progress else False

        return render(request, 'progres_tracker/character_progress_view.html', {
            'character': character,
            'quests': quests,
            'progress_dict': progress_dict,
            'quest_completed_dict': quest_completed_dict,
        })


class CommentUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk, user=request.user)
        form = CommentForm(instance=comment)
        return render(request, 'progres_tracker/comment_form.html', {'form': form, 'comment': comment})

    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk, user=request.user)
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('quest_detail', pk=comment.quest.pk)
        return render(request, 'progres_tracker/comment_form.html', {'form': form, 'comment': comment})


class CommentDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk, user=request.user)
        return render(request, 'progres_tracker/comment_confirm_delete.html', {'comment': comment})

    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk, user=request.user)
        quest_pk = comment.quest.pk
        comment.delete()
        messages.success(request, 'Comment deleted successfully')
        return redirect('quest_detail', pk=quest_pk)


@login_required
def quest_search(request):
    query = request.GET.get('q')
    if query:
        quests = Quest.objects.filter(name__icontains=query)
    else:
        quests = Quest.objects.all()

    html = render_to_string('progres_tracker/partials/quest_list.html', {'quests': quests, 'user': request.user})
    return JsonResponse({'html': html})



def character_search(request):
    query = request.GET.get('q', '')
    characters = Character.objects.filter(name__icontains=query)
    html = render_to_string('progres_tracker/partials/character_list.html', {'characters': characters})
    return JsonResponse({'html': html})


def quest_filter(request):
    game = request.GET.get('game', 'all')
    if game == 'all':
        quests = Quest.objects.all()
    else:
        quests = Quest.objects.filter(game__name__icontains=game)
    context = {
        'quests': quests,
        'user': request.user,  # Ensure user context is passed
    }
    return JsonResponse({'html': render_to_string('progres_tracker/partials/quest_list.html', context)})