# Full CBT Django Project (Enhanced)

## Features
- User signup/login (Django auth)
- Admin panel with CSV import for bulk questions
- Models: Subject, Quiz, Question, Choice, Attempt
- Timed quizzes (client-side countdown) and duration tracking
- Randomized selection of questions per quiz
- Student dashboard to see attempts
- Sample CSV included: sample_questions.csv

## Quick start
1. python -m venv venv
2. source venv/bin/activate  # Windows: venv\Scripts\activate
3. pip install -r requirements.txt
4. python manage.py migrate
5. python manage.py createsuperuser
6. python manage.py runserver
7. Open http://127.0.0.1:8000/ and /admin/
8. http://127.0.0.1:8000/class-results/


## CSV format
Headers: quiz,question_text,choice1,choice2,choice3,choice4,choice5,correct_choice,marks
