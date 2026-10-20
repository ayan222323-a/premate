from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import TestSelectForm
from .models import TestAttempt, AttemptQuestion
from .services import generate_mcqs


@login_required
def exam_select(request):
    if request.method == 'POST':
        form = TestSelectForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            difficulty = form.cleaned_data['difficulty']
            count = form.cleaned_data['count']
            try:
                mcqs = generate_mcqs(subject, difficulty, count)
            except Exception as e:
                print('MCQ ERROR:', repr(e))
                messages.error(request, f'Questions nahi ban paye: {e}')
                return redirect('exam_select')

            attempt = TestAttempt.objects.create(
                user=request.user, subject=subject,
                difficulty=difficulty, total=len(mcqs),
            )
            for m in mcqs:
                AttemptQuestion.objects.create(
                    attempt=attempt, text=m['question'], options=m['options'],
                    correct_index=m['answer_index'], explanation=m['explanation'],
                    subtopic=m['subtopic'],
                )
            return redirect('take_test', attempt_id=attempt.id)
    else:
        form = TestSelectForm()
    return render(request, 'exams/select.html', {'form': form})


@login_required
def take_test(request, attempt_id):
    attempt = get_object_or_404(TestAttempt, id=attempt_id, user=request.user)
    if attempt.completed:
        return redirect('test_result', attempt_id=attempt.id)

    questions = list(attempt.questions.order_by('id'))

    if request.method == 'POST':
        score = 0
        for q in questions:
            val = request.POST.get(f'q_{q.id}')
            if val is not None and val.isdigit() and int(val) < len(q.options):
                q.selected_index = int(val)
                q.save()
            if q.selected_index == q.correct_index:
                score += 1
        attempt.score = score
        attempt.completed = True
        attempt.save()
        return redirect('test_result', attempt_id=attempt.id)

    return render(request, 'exams/take.html', {'attempt': attempt, 'questions': questions})


@login_required
def test_result(request, attempt_id):
    attempt = get_object_or_404(TestAttempt, id=attempt_id, user=request.user)
    if not attempt.completed:
        return redirect('take_test', attempt_id=attempt.id)

    rows = []
    topics = {}
    for q in attempt.questions.order_by('id'):
        is_correct = q.selected_index == q.correct_index
        rows.append({
            'q': q,
            'selected': q.options[q.selected_index] if q.selected_index is not None else None,
            'correct': q.options[q.correct_index],
            'is_correct': is_correct,
        })
        t = topics.setdefault(q.subtopic or 'General', [0, 0])
        t[1] += 1
        if is_correct:
            t[0] += 1

    topic_rows = [{'name': k, 'correct': v[0], 'total': v[1]} for k, v in topics.items()]
    percent = round(attempt.score / attempt.total * 100) if attempt.total else 0

    return render(request, 'exams/result.html', {
        'attempt': attempt, 'rows': rows,
        'topic_rows': topic_rows, 'percent': percent,
    })