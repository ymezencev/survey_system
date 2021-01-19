from itertools import islice

from django.db.models import F
from rest_framework import serializers

from survey.models import Survey, Question, Choice, SurveyResult, Answer


class ChoiceSerializer(serializers.ModelSerializer):
    """Список доступных ответов на вопрос"""
    class Meta:
        model = Choice
        fields = ["id", "text", ]


class QuestionSerializer(serializers.ModelSerializer):
    """Список вопросов"""
    choices = ChoiceSerializer(read_only=True, many=True)

    class Meta:
        model = Question
        fields = ["id", "type", "order_num", "text", "choices"]


class AvailableSurveySerializer(serializers.ModelSerializer):
    """Список активных опросов"""
    questions = QuestionSerializer(read_only=True, many=True)

    class Meta:
        model = Survey
        fields = ["id", "name", "description", "start_at", "finish_at",
                  "questions", ]


class AnswerListSerializer(serializers.ModelSerializer):
    """Результат опроса. Ответы на опрос"""
    question = QuestionSerializer(read_only=True)

    class Meta:
        model = Answer
        fields = ["id", "question", "choice", "text", ]


class SurveyDataSerializer(serializers.ModelSerializer):
    """Данные по опросу в результате прохождение"""

    class Meta:
        model = Survey
        fields = ["id", "name", "description"]


class SurveyListSerializer(serializers.ModelSerializer):
    """Результат опроса"""
    answers = AnswerListSerializer(many=True)
    survey = SurveyDataSerializer(read_only=True)

    class Meta:
        model = SurveyResult
        fields = ["id", "survey", "user", "created_at", "answers", ]


class AnswerSerializer(serializers.ModelSerializer):
    """Ответы на опрос"""

    class Meta:
        model = Answer
        fields = ["question", "choice", "text", ]


class SurveySerializer(serializers.ModelSerializer):
    """Опрос"""
    answers = AnswerSerializer(many=True)
    # todo
    # сейчас выводится список ответов и вопрос для каждого из ответов,
    # а хотелось бы список вопросов и список ответов для каждого из ответов
    # задал вопрос на stackoverflow
    # https://stackoverflow.com/questions/65770122/how-to-group-child-as-a-nested-list-for-each-parent

    class Meta:
        model = SurveyResult
        fields = ["survey", "user", "created_at", "answers", ]

    def validate(self, data):
        """
        Проерка переданных ответов
        Необходимо обязательно передать все ответы и проверить,
        что корректно переданы варианты ответов
        Для вопроса с типом choice, text возможно передать только один ответ
        """
        survey_questions = Survey.objects.filter(
            id=data["survey"].id).values(
                question_id=F("questions__id"),
                question_type=F("questions__type"),
                choice_id=F("questions__choices__id"))

        if len(survey_questions) == 0:
            raise serializers.ValidationError("Не найден опрос")

        answers = [{"question_id": answer.get("question").id,
                    "choice_id": getattr(answer.get("choice"), "id", None)}
                   for answer in data["answers"]]
        required_questions_ids = set(q["question_id"]
                                     for q in survey_questions)
        passed_questions_ids = list(q["question_id"] for q in answers)
        passed_questions_ids_set = set(passed_questions_ids)

        # переданы все вопросы без дублей
        if required_questions_ids != passed_questions_ids_set or \
                len(required_questions_ids) != len(passed_questions_ids_set):
            raise serializers.ValidationError(
                "Некорректно заполнены ответы на вопрсы")

        keys_to_keep = ['question_id', 'choice_id']
        survey_questions_no_type = [{key: item[key] for key in keys_to_keep}
                                    for item in survey_questions]
        unique_choices = set(
            frozenset(i.items()) for i in answers)

        # переданные варианты ответов пренадлежат вопросам
        # нет дублей вариантов ответов
        if (not all(val in survey_questions_no_type for val in answers)) or \
                len(unique_choices) != len(answers):
            raise serializers.ValidationError(
                "Некорректно заполнены варианты ответов")

        # choice, text только один ответ
        for question in survey_questions:
            if question["question_type"] != "choice_multiple":
                cnt = 0
                for answer in answers:
                    if answer["question_id"] == question["question_id"]:
                        cnt += 1
                if cnt > 1:
                    raise serializers.ValidationError(
                        "Запрещено передавать несколько вариантов ответа "
                        "на вопрос с типом \"текст\" \"Единственный выбор\"")

        return data

    def create(self, validated_data):
        """Cохранение результатов опроса и ответов"""
        answers_data = validated_data.pop("answers")
        survey_result = SurveyResult.objects.create(**validated_data)
        for item in answers_data:
            item.update({"survey_result": survey_result})

        batch_size = 50
        answers_objs = (Answer(**obj) for obj in answers_data)
        while True:
            batch = list(islice(answers_objs, batch_size))
            if not batch:
                break
            Answer.objects.bulk_create(batch, batch_size)

        return survey_result
