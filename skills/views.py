from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Skill, Category, Review
from .forms import SkillForm, RegisterForm, ReviewForm


def home(request):
    recent_skills = Skill.objects.select_related('user', 'category').order_by('-created_at')[:6]
    categories = Category.objects.all()
    total_skills = Skill.objects.count()
    return render(request, 'home.html', {
        'recent_skills': recent_skills,
        'categories': categories,
        'total_skills': total_skills,
    })


# Extension 1: Search by title or category
# How it works:
#   1. The user types a query into the search box and/or picks a category.
#   2. Both are sent as GET parameters (?q=...&category=...) in the URL.
#   3. We read those values with request.GET.get() — no database write needed.
#   4. Q objects let us search across multiple fields with OR logic.
#   5. Category filtering is a simple .filter() on the FK slug.
#   6. The view passes everything back to the template so the form stays filled in.
def skill_list(request):
    skills = Skill.objects.select_related('user', 'category').order_by('-created_at')
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()

    if query:
        # Q objects allow OR filtering across multiple fields
        skills = skills.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    if category_slug:
        skills = skills.filter(category__slug=category_slug)

    categories = Category.objects.all()
    return render(request, 'skills/skill_list.html', {
        'skills': skills,
        'query': query,
        'categories': categories,
        'selected_category': category_slug,
        'result_count': skills.count(),
    })


def skill_detail(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    reviews = skill.reviews.select_related('reviewer').order_by('-created_at')
    user_review = None
    review_form = None

    if request.user.is_authenticated:
        user_review = reviews.filter(reviewer=request.user).first()
        # Only show the form if the user hasn't reviewed yet and doesn't own the skill
        if user_review is None and request.user != skill.user:
            review_form = ReviewForm()

    return render(request, 'skills/skill_detail.html', {
        'skill': skill,
        'reviews': reviews,
        'user_review': user_review,
        'review_form': review_form,
    })


@login_required
def skill_create(request):
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)  # don't save yet — attach the user first
            skill.user = request.user
            skill.save()
            messages.success(request, 'Your skill has been posted!')
            return redirect('skill_detail', pk=skill.pk)
    else:
        form = SkillForm()
    return render(request, 'skills/skill_form.html', {'form': form, 'action': 'Post'})


@login_required
def skill_edit(request, pk):
    # get_object_or_404 with user= ensures only the owner can edit
    skill = get_object_or_404(Skill, pk=pk, user=request.user)
    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Skill updated successfully!')
            return redirect('skill_detail', pk=skill.pk)
    else:
        form = SkillForm(instance=skill)
    return render(request, 'skills/skill_form.html', {
        'form': form,
        'action': 'Edit',
        'skill': skill,
    })


@login_required
def skill_delete(request, pk):
    skill = get_object_or_404(Skill, pk=pk, user=request.user)
    if request.method == 'POST':
        skill.delete()
        messages.success(request, 'Skill deleted.')
        return redirect('dashboard')
    return render(request, 'skills/skill_confirm_delete.html', {'skill': skill})


@login_required
def dashboard(request):
    skills = Skill.objects.filter(user=request.user).order_by('-created_at')
    total_reviews = Review.objects.filter(skill__user=request.user).count()
    return render(request, 'skills/dashboard.html', {
        'skills': skills,
        'total_reviews': total_reviews,
    })


def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # log the user in immediately after signup
            messages.success(request, f'Welcome to Campus SkillSwap, {user.username}!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


# Extension 3: Review & Rating System
# How it works:
#   1. Only logged-in users can submit a review (enforced by @login_required).
#   2. Users cannot review their own skill.
#   3. The unique_together constraint on the model prevents duplicate reviews,
#      but we check in the view too so we can show a friendly message.
#   4. The form is submitted to this URL via POST, then we redirect back to
#      the skill detail page — the "Post/Redirect/Get" pattern prevents
#      double-submission on browser refresh.
@login_required
def add_review(request, pk):
    skill = get_object_or_404(Skill, pk=pk)

    if request.user == skill.user:
        messages.error(request, "You can't review your own skill.")
        return redirect('skill_detail', pk=pk)

    if Review.objects.filter(skill=skill, reviewer=request.user).exists():
        messages.error(request, "You've already reviewed this skill.")
        return redirect('skill_detail', pk=pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.skill = skill
            review.reviewer = request.user
            review.save()
            messages.success(request, 'Your review has been submitted!')
        else:
            messages.error(request, 'Please fill in all required fields.')

    return redirect('skill_detail', pk=pk)
