from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from survey.models import Survey, Question, Choice


class EditLinkToInlineObject(object):
    """Добавить возможность редактирования вложенных моделей в админке"""
    def edit_link(self, instance):
        url = reverse('admin:%s_%s_change' % (
            instance._meta.app_label, instance._meta.model_name),
            args=[instance.pk])
        if instance.pk:
            return mark_safe(u'<a href="{u}">Редактировать</a>'.format(u=url))
        else:
            return ''
    edit_link.short_description = "Редактирование"


class QuestionInline(EditLinkToInlineObject, admin.StackedInline):
    """Вопросы на странице создания/редактирования опроса"""
    model = Question
    extra = 0
    fields = ("edit_link", "type", "order_num", "text",)
    readonly_fields = ('edit_link', )


class ChoiceInline(admin.StackedInline):
    """Варианты ответов на вопрос на странице редактирования вопроса"""
    model = Choice
    extra = 0


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    """Доступные опросы"""
    list_display = ("name", "start_at", "finish_at",)
    list_display_links = ("name",)
    list_filter = ("start_at", "finish_at")
    search_fields = ("name",)
    fields = ("name", ("start_at", "finish_at",),)
    inlines = [QuestionInline, ]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ("start_at",)
        return self.readonly_fields


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Вопросы в опросе и варианты ответов"""
    fields = ("type", "text", "order_num", "survey")
    inlines = [ChoiceInline, ]

    def get_inline_instances(self, request, obj=None):
        if obj and obj.type == "text":
            return []
        return super(QuestionAdmin, self).get_inline_instances(request, obj)
