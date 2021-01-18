# Created Yuri Mezentsev 2021-01-17 11:20
import datetime

from django.db import migrations, transaction


def create_rate_survey(apps, schema_editor):
    """
    Создание опроса по оценке приложения с момента запуска на 100 дней
    Создание завершённых опросов
    Создание пользователей системы
    """

    Survey = apps.get_model("survey", "Survey")
    Question = apps.get_model("survey", "Question")
    Choice = apps.get_model("survey", "Choice")
    today = datetime.date.today()
    duration = datetime.timedelta(days=100)

    survey = Survey(name="Is this survey system OK?",
                    start_at=today, finish_at=today+duration)
    survey.save()

    q1 = Question(survey=survey, type="choice", order_num=1, text="Models design")
    q1.save()
    c1 = Choice(text="Ok", question=q1)
    c2 = Choice(text="Not ok", question=q1)
    c3 = Choice(text="Coud have added MTM to question-choice (in case of similar choices for many questions for example: (1,2,3,4,5 marks), (perfect, good, bad marks))", question=q1)
    c4 = Choice(text="MTM is not necessary new choices for every question is enough.", question=q1)

    q2 = Question(survey=survey, type="choice", order_num=2, text="Serializers design")
    q2.save()
    c5 = Choice(text="Fine", question=q2)
    c6 = Choice(text="Perfect", question=q2)
    c7 = Choice(text="Not good", question=q2)
    c8 = Choice(text="Used two similar serializers Answer and AnswerList for create and get survey "
                     "(Dont know if it's ok but api document for front-end looks better.)", question=q2)

    q3 = Question(survey=survey, type="choice", order_num=3, text="Views design")
    q3.save()
    c9 = Choice(text="Ok", question=q3)
    c10 = Choice(text="Perfect", question=q3)
    c11 = Choice(text="Very very bad", question=q3)

    q4 = Question(survey=survey, type="choice", order_num=4, text="Tests quality")
    q4.save()
    c12 = Choice(text="Ok", question=q4)
    c13 = Choice(text="Perfect", question=q4)
    c14 = Choice(text="Very very bad", question=q4)
    c15 = Choice(text="Should be done absolutely differently...", question=q4)

    q5 = Question(survey=survey, type="choice", order_num=5, text="Documentation quality")
    q5.save()
    c16 = Choice(text="Ok", question=q5)
    c17 = Choice(text="Perfect", question=q5)
    c18 = Choice(text="Very very bad", question=q5)
    c19 = Choice(text="So so, need more information", question=q5)

    q6 = Question(survey=survey, type="text", order_num=6, text="Conclusion. Is this survey system OK? Describe a few things to work on to improve the system.")
    q6.save()

    q7 = Question(survey=survey, type="choice_multiple", order_num=7, text="Choose your options")
    q7.save()
    c20 = Choice(text="I just wanna check how it works.", question=q7)
    c21 = Choice(text="I am not professional.", question=q7)
    c22 = Choice(text="I was lazy to give full review in last question.", question=q7)
    c23 = Choice(text="I like the app", question=q7)
    c24 = Choice(text="I don't like the app", question=q7)

    choices = [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14,
               c15, c16, c17, c18, c19, c20, c21, c22, c23, c24]
    # Choice.objects.bulk_create(choices) # todo: can't save bulk_create twice
    for c in choices:
        c.save()

    # Создадим пользователй
    User = apps.get_model("auth", "User")
    user_data1 = {
        'username': 'first_user',
        'email': 'test_user1@gmail.com'
    }
    user1 = User(**user_data1)
    user1.save()

    user_data2 = {
        'username': 'second_user',
        'email': 'test_user2@gmail.com'
    }
    user2 = User(**user_data2)
    user2.save()

    # Прохождение опроса
    SurveyResult = apps.get_model("survey", "SurveyResult")
    Answer = apps.get_model("survey", "Answer")

    # Анонимный пользователь
    sr = SurveyResult(survey=survey, user=None)
    sr.save()

    a1 = Answer(survey_result=sr, question=q1, choice=c1, text=None)
    a2 = Answer(survey_result=sr, question=q2, choice=c6, text=None)
    a3 = Answer(survey_result=sr, question=q3, choice=c10, text=None)
    a4 = Answer(survey_result=sr, question=q4, choice=c13, text=None)
    a5 = Answer(survey_result=sr, question=q5, choice=c17, text=None)
    a6 = Answer(survey_result=sr, question=q6, choice=None, text="No user. Text answer. Text answer. Text answer. Text answer. Text answer. Text answer. Text answer. ")
    a71 = Answer(survey_result=sr, question=q7, choice=c20, text=None)
    a72 = Answer(survey_result=sr, question=q7, choice=c21, text=None)
    a73 = Answer(survey_result=sr, question=q7, choice=c22, text=None)

    answers = [a1, a2, a3, a4, a5, a6, a71, a72, a73]
    Answer.objects.bulk_create(answers)

    # user1 пользователь
    sru1 = SurveyResult(survey=survey, user=user1)
    sru1.save()

    au1 = Answer(survey_result=sru1, question=q1, choice=c2, text=None)
    au2 = Answer(survey_result=sru1, question=q2, choice=c5, text=None)
    au3 = Answer(survey_result=sru1, question=q3, choice=c11, text=None)
    au4 = Answer(survey_result=sru1, question=q4, choice=c13, text=None)
    au5 = Answer(survey_result=sru1, question=q5, choice=c18, text=None)
    au6 = Answer(survey_result=sru1, question=q6, choice=None, text="USER 1 Text answer. Text answer. Text answer. Text answer. Text answer. Text answer. Text answer. ")
    au71 = Answer(survey_result=sru1, question=q7, choice=c20, text=None)
    au72 = Answer(survey_result=sru1, question=q7, choice=c21, text=None)

    answers_u1 = [au1, au2, au3, au4, au5, au6, au71, au72]
    Answer.objects.bulk_create(answers_u1)

    # user2 пользователь
    sru2 = SurveyResult(survey=survey, user=user2)
    sru2.save()

    auu1 = Answer(survey_result=sru2, question=q1, choice=c1, text=None)
    auu2 = Answer(survey_result=sru2, question=q2, choice=c5, text=None)
    auu3 = Answer(survey_result=sru2, question=q3, choice=c11, text=None)
    auu4 = Answer(survey_result=sru2, question=q4, choice=c13, text=None)
    auu5 = Answer(survey_result=sru2, question=q5, choice=c19, text=None)
    auu6 = Answer(survey_result=sru2, question=q6, choice=None, text="USER 2 Text answer. Text answer. Text answer. Text answer. Text answer. Text answer. Text answer. ")
    auu71 = Answer(survey_result=sru2, question=q7, choice=c21, text=None)

    answers_u2 = [auu1, auu2, auu3, auu4, auu5, auu6, auu71]
    Answer.objects.bulk_create(answers_u2)


def rollback_rate_survey(apps, schema_editor):
    Survey = apps.get_model("survey", "Survey")
    survey = Survey.objects.get(name="Is this survey system OK?")
    survey.delete()

    User = apps.get_model("auth", "User")
    user1 = User.objects.get(username="first_user")
    user1.delete()
    user2 = User.objects.get(username="second_user")
    user2.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_rate_survey, rollback_rate_survey),
    ]
