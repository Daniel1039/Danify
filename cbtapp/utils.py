from .models import Question


def get_or_create_question(quiz, subject, row):
    """
    Creates a Question only if a matching one doesn't already exist,
    so re-uploading the same CSV/Excel file won't create duplicates.
    Matches on: quiz, subject, text, options, correct_option, marks, explanation.
    Returns (question, created_bool)
    """
    text = str(row.get('question_text') or row.get('text') or '').strip()
    option_a = str(row.get('option_a') or '').strip()
    option_b = str(row.get('option_b') or '').strip()
    option_c = str(row.get('option_c') or '').strip()
    option_d = str(row.get('option_d') or '').strip()
    correct_option = str(row.get('correct_option') or 'A').strip().upper()
    marks = int(row.get('marks') or 1)
    explanation = str(row.get('explanation') or '').strip()

    existing = Question.objects.filter(
        quiz=quiz,
        subject=subject,
        text=text,
        option_a=option_a,
        option_b=option_b,
        option_c=option_c,
        option_d=option_d,
        correct_option=correct_option,
        marks=marks,
        explanation=explanation,
    ).first()

    if existing:
        return existing, False

    question = Question.objects.create(
        quiz=quiz,
        subject=subject,
        passage=str(row.get('passage') or ''),
        text=text,
        option_a=option_a,
        option_b=option_b,
        option_c=option_c,
        option_d=option_d,
        correct_option=correct_option,
        marks=marks,
        explanation=explanation,
    )
    return question, True