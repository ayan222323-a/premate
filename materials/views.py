from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from exams.models import TestAttempt, AttemptQuestion
from exams.services import generate_mcqs
from .models import StudyNote
from .services import generate_notes


@login_required
def material_list(request):
    stats = {}
    questions = AttemptQuestion.objects.filter(attempt__user=request.user, attempt__completed=True)
    for q in questions:
        name = q.subtopic or q.attempt.subject
        t = stats.setdefault(name, [0, 0])
        t[1] += 1
        if q.selected_index == q.correct_index:
            t[0] += 1

    weak = [
        {'name': k, 'percent': round(v[0] / v[1] * 100), 'total': v[1]}
        for k, v in stats.items() if round(v[0] / v[1] * 100) < 60
    ]
    weak.sort(key=lambda t: t['percent'])

    notes = StudyNote.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'materials/list.html', {
        'weak': weak,
        'notes': notes,
        'has_data': bool(stats),
    })


@login_required
def note_detail(request):
    topic = request.GET.get('topic', '').strip()[:100]
    if not topic:
        return redirect('materials')

    note = StudyNote.objects.filter(user=request.user, topic=topic).first()
    if note is None:
        try:
            content = generate_notes(topic)
        except Exception as e:
            print('NOTES ERROR:', repr(e))
            messages.error(request, f'Notes nahi ban paye: {e}')
            return redirect('materials')
        note = StudyNote.objects.create(user=request.user, topic=topic, content=content)

    return render(request, 'materials/detail.html', {'note': note})


@login_required
@require_POST
def practice_topic(request):
    topic = request.POST.get('topic', '').strip()[:100]
    if not topic:
        return redirect('materials')

    try:
        mcqs = generate_mcqs(topic, 'Medium', 5)
    except Exception as e:
        print('MCQ ERROR:', repr(e))
        messages.error(request, f'Questions nahi ban paye: {e}')
        return redirect('materials')

    attempt = TestAttempt.objects.create(
        user=request.user, subject=topic, difficulty='Medium', total=len(mcqs),
    )
    for m in mcqs:
        AttemptQuestion.objects.create(
            attempt=attempt, text=m['question'], options=m['options'],
            correct_index=m['answer_index'], explanation=m['explanation'],
            subtopic=m['subtopic'] or topic,
        )
    return redirect('take_test', attempt_id=attempt.id)