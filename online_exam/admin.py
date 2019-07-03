# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import course, user, topic, subtopic, question_type, level, exam_detail, question_bank,  option, answer, registration, result
# Register your models here.
admin.site.register(course)
admin.site.register(user)
admin.site.register(topic)
admin.site.register(subtopic)
admin.site.register(question_type)
admin.site.register(level)
admin.site.register(exam_detail)
admin.site.register(question_bank)
admin.site.register(option)
admin.site.register(answer)
admin.site.register(registration)
admin.site.register(result)

