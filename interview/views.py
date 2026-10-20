from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ResumeUploadForm
from .models import InterviewSession, InterviewQA
from .services import extract_text_from_pdf, generate_questions, evaluate_answer


@login_required
def upload_resume(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()
            try:
                resume.extracted_text = extract_text_from_pdf(resume.file.path)
            except Exception:
                resume.extracted_text = ''
            finally:
                # Render disk is ephemeral: delete file from disk, keeping DB row
                if resume.file:
                    try:
                        resume.file.storage.delete(resume.file.name)
                    except Exception:
                        pass
            resume.save()

            if not resume.extracted_text:
                messages.error(request, 'PDF se text nahi nikla. Text-based PDF upload karo.')
                return redirect('upload_resume')

            session = InterviewSession.objects.create(
                user=request.user,
                resume=resume,
                job_role=form.cleaned_data['job_role'],
            )

            try:
                questions = generate_questions(resume.extracted_text, session.job_role)
            except Exception as e:
                print("AI ERROR:", repr(e))
                session.delete()
                messages.error(request, f'AI se questions nahi aaye: {e}')
                return redirect('upload_resume')

            for q in questions:
                InterviewQA.objects.create(session=session, question=q)
            return redirect('interview_room', session_id=session.id)
    else:
        form = ResumeUploadForm()
    return render(request, 'interview/upload.html', {'form': form})


@login_required
def interview_room(request, session_id):
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    qas = list(session.qas.order_by('id'))
    total = len(qas)
    current = next((qa for qa in qas if not qa.answer), None)

    if current is None:
        return redirect('session_detail', session_id=session.id)

    if request.method == 'POST':
        answer = request.POST.get('answer', '').strip()
        if answer:
            current.answer = answer
            current.save()
        return redirect('interview_room', session_id=session.id)

    number = qas.index(current) + 1
    return render(request, 'interview/room.html', {
        'session': session,
        'qa': current,
        'number': number,
        'total': total,
        'percent': int((number - 1) / total * 100),
    })


@login_required
def session_detail(request, session_id):
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    qas = list(session.qas.order_by('id'))

    for qa in qas:
        if qa.answer and not qa.feedback:
            qa.score, qa.feedback = evaluate_answer(qa.question, qa.answer, session.job_role)
            qa.save()

    scored = [qa.score for qa in qas if qa.score is not None]
    if scored and session.overall_score is None:
        session.overall_score = round(sum(scored) / len(scored), 1)
        session.save()

    return render(request, 'interview/session_detail.html', {
        'session': session,
        'qas': qas,
    })