from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q


class Survey(models.Model):
    """Доступные опросы"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.first_start_at = self.start_at

    name = models.CharField("Название опроса", max_length=150)
    description = models.TextField("Описание опроса", max_length=300,
                                   null=True, blank=True)
    start_at = models.DateTimeField("Начало действия опроса", db_index=True)
    finish_at = models.DateTimeField("Окончание действия опроса",
                                     db_index=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        is_creating = not self.pk
        # Условие - время начала действия опроса нельзя изменять
        if not is_creating and self.start_at != self.first_start_at:
            raise ValueError("Нельзя изменять время начала действия опроса")

        # Период действия опроса должен быть корректным
        if self.start_at >= self.finish_at:
            raise ValueError(
                f"Некорректный период дейтсвия опроса "
                f"(start: {self.start_at}; finihsh: {self.finish_at})")
        super().save(*args, **kwargs)


class Question(models.Model):
    """Вопросы в опросах"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.old_type = self.type

    QUESTION_TYPE = (
        ("text", "Текст"),
        ("choice", "Один вариант ответа"),
        ("choice_multiple", "Несколько вариантов ответа")
    )

    text = models.TextField("Текст вопроса", max_length=300)
    type = models.CharField("Тип вопроса", max_length=15,
                            choices=QUESTION_TYPE)
    order_num = models.IntegerField("Номер вопроса")
    survey = models.ForeignKey(Survey, verbose_name="Опрос",
                               related_name="questions",
                               on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['order_num', 'survey_id'],
                name='%(app_label)s_%(class)s_unique_order'),
            models.CheckConstraint(
                check=(Q(order_num__gt=0)),
                name="%(app_label)s_%(class)s_order_num__gt_0")
        ]

    def __str__(self):
        return self.text

    def save(self, *args, **kwargs):
        is_creating = not self.pk

        # Запрещено изменение типа вопроса вида:
        # текстовой ответ -> другие типы и другие типы -> текстовой ответ
        if not is_creating \
                and (self.old_type == "text" and self.type != "text"
                     or self.old_type != "text" and self.type == "text"):
            raise ValueError(f"Ошибка при изменении типа вопроса "
                             f"{self.old_type} -> {self.type}")
        super().save(*args, **kwargs)


class Choice(models.Model):
    """Вариант ответа в вопросе"""

    text = models.CharField("Вариант ответа", max_length=300)
    question = models.ForeignKey(Question, verbose_name="Вопрос",
                                 related_name="choices",
                                 on_delete=models.CASCADE)

    def __str__(self):
        return self.text

    def save(self, *args, **kwargs):
        # У вопроса типа "текстовой ответ" не должно быть вариантов ответа
        if self.question.type == "text":
            raise ValueError("Невозможно сохранить варианты ответа "
                             "для вопроса с типом текст")
        super().save(*args, **kwargs)


class SurveyResult(models.Model):
    """
    Пройденные опросы. Привязка ответов к конкретному прохождению опроса
    (Отслеживать пройденные опроса анонимных пользователей)
    """

    survey = models.ForeignKey(Survey, verbose_name="Опрос",
                               related_name="results",
                               on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, blank=True,
                             verbose_name="Пользователь",
                             related_name="surveys",
                             on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField("Окончание действия опроса",
                                      auto_now_add=True, db_index=True)

    def __str__(self):
        return f"{self.id}) {self.survey.name} {self.created_at}"


class Answer(models.Model):
    """Ответы пользователей"""
    survey_result = models.ForeignKey(SurveyResult,
                                      verbose_name="Пройденный опрос",
                                      related_name="answers",
                                      on_delete=models.CASCADE)
    question = models.ForeignKey(Question, verbose_name="Вопрос",
                                 related_name="answers",
                                 on_delete=models.DO_NOTHING)
    choice = models.ForeignKey(Choice, verbose_name="Вариант ответа",
                               related_name="answer_choices",
                               null=True, blank=True,
                               on_delete=models.DO_NOTHING,
                               default=None)

    text = models.CharField("Текстовой ответ", max_length=300,
                            null=True, blank=True, default=None)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(choice__isnull=False) | Q(text__isnull=False),
                name='not_both_answer_options_null'
            )
        ]

    def __str__(self):
        return f"{self.choice.id} {self.text}"

    def save(self, *args, **kwargs):
        # Только один ответ на вопрос с типом choice

        if self.question.type == "choice":
            answers_cnt = Answer.objects.filter(
                survey_result=self.survey_result,
                question=self.question).count()
            if answers_cnt != 0:
                raise ValueError("Невозможно сохранить несколько вариантов "
                                 "ответа для вопроса с единственным выбором")
        super().save(*args, **kwargs)
