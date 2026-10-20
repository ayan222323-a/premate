from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from exams.models import TestAttempt, AttemptQuestion
from interview.models import InterviewSession
from .utils import calculate_streak


@login_required
def progress_dashboard(request):
    user = request.user

    attempts = list(TestAttempt.objects.filter(user=user, completed=True).order_by('created_at'))
    sessions = list(InterviewSession.objects.filter(user=user, overall_score__isnull=False).order_by('created_at'))

    # Test stats
    percents = [round(a.score / a.total * 100) for a in attempts if a.total]
    total_tests = len(attempts)
    avg_percent = round(sum(percents) / len(percents)) if percents else 0
    best_percent = max(percents) if percents else 0

    # Line chart data (last 15 tests)
    recent = attempts[-15:]
    line_labels = [timezone.localtime(a.created_at).strftime('%d %b') for a in recent]
    line_values = [round(a.score / a.total * 100) if a.total else 0 for a in recent]

    # Topic-wise accuracy
    topic_stats = {}
    questions = AttemptQuestion.objects.filter(attempt__user=user, attempt__completed=True)
    for q in questions:
        name = q.subtopic or q.attempt.subject
        t = topic_stats.setdefault(name, [0, 0])
        t[1] += 1
        if q.selected_index == q.correct_index:
            t[0] += 1

    topics = [
        {'name': k, 'correct': v[0], 'total': v[1], 'percent': round(v[0] / v[1] * 100)}
        for k, v in topic_stats.items()
    ]
    topics.sort(key=lambda t: t['percent'])
    weak_topics = [t for t in topics if t['percent'] < 60][:5]
    strong_topics = [t for t in reversed(topics) if t['percent'] >= 80][:5]

    chart_topics = topics[:10]
    bar_labels = [t['name'] for t in chart_topics]
    bar_values = [t['percent'] for t in chart_topics]

    # Interview stats
    interview_scores = [s.overall_score for s in sessions]
    avg_interview = round(sum(interview_scores) / len(interview_scores), 1) if interview_scores else None

    # Streak
    active_days = {timezone.localtime(a.created_at).date() for a in attempts}
    active_days |= {timezone.localtime(s.created_at).date() for s in sessions}
    streak = calculate_streak(active_days)

    return render(request, 'progress/progress.html', {
        'total_tests': total_tests,
        'avg_percent': avg_percent,
        'best_percent': best_percent,
        'streak': streak,
        'avg_interview': avg_interview,
        'total_interviews': len(sessions),
        'weak_topics': weak_topics,
        'strong_topics': strong_topics,
        'recent_attempts': list(reversed(attempts))[:5],
        'recent_sessions': list(reversed(sessions))[:5],
        'line_labels': line_labels,
        'line_values': line_values,
        'bar_labels': bar_labels,
        'bar_values': bar_values,
    })