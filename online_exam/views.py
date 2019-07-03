# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.decorators.csrf import csrf_exempt
import datetime
import json
import math
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.db.models import Sum
import requests
from .models import course, user, topic, subtopic, question_type, level, exam_detail, question_bank,  option, answer, registration, result, MatchTheColumns

def faculty_dashboard(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0):
        registrations = []
        for i in registration.objects.values("exam_id").distinct():
            regis = dict()
            regis["exam_name"] = exam_detail.objects.get(pk = i["exam_id"]).exam_name
            regis["count"] = registration.objects.filter(exam_id = i["exam_id"]).count()
            registrations.append(regis)
        now = datetime.datetime.now()
        curr = str(now.year) + "-" + str(now.month) + "-01"
        curr_year = int(now.year)
        curr_month = int(now.month)
        dataArray = []
        for i in range(0, 6):
            if(curr_month-i <= 0):
                curr_year -= 1
                curr_month += 12
            curr_array = dict()
            curr_array["year"] = curr_year
            curr_array["month"] = curr_month - i -1
            if(curr_month - i != 12):
                curr_array["count"] = user.objects.filter(created__range = (datetime.date(curr_year, curr_month-i, 1), datetime.date(curr_year, curr_month-i + 1, 1))).count()
            else:
                curr_array["count"] = user.objects.filter(created__range = (datetime.date(curr_year, 12, 1), datetime.date(curr_year+1, 1, 1))).count()
            dataArray.append(curr_array)
        pass_p = 0
        count = 0
        for i in registration.objects.filter(answered=1).all():
            gained_score = result.objects.filter(registration_id = i).aggregate(Sum('score'))
            if(gained_score['score__sum'] == None):
                gained_score = 0
            else:
                gained_score = int(gained_score['score__sum'])
            total_score = 0
            for j in result.objects.filter(registration_id = i).all():
                total_score += j.question_id.score
            if(gained_score >= i.exam_id.pass_percentage*total_score/100):
                pass_p += 1
            count += 1
        if(count == 0):
            pass_percentage = 0
        else:
            pass_percentage = pass_p*100/count
        return render(request ,'online_exam/faculty_dashboard.html', {"num_of_users":user.objects.count(), "num_of_exams":exam_detail.objects.count(), "num_of_questions":question_bank.objects.count(), "registrations":registrations, "dataArray":dataArray, "pass_percentage":pass_percentage})
    else:
        return redirect("../login")

@csrf_exempt
def faculty_add_course(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0):
        if request.method=="POST":
            temp = course()
            temp.course_name = request.POST['course_name']
            temp.description = request.POST['description']
            temp.faculty = request.POST['faculty']
            print(temp)
            if(course.objects.filter(course_name=temp.course_name).count() == 0):
                temp.save()
                message = "Course was successfully added!!"
                return render(request ,'online_exam/faculty_add_course.html',{"message":message})
            else:
                wrong_message = "Sorry, course already exists!!"
                return render(request,'online_exam/faculty_add_course.html',{"wrong_message":wrong_message})
        else:
            return render(request,'online_exam/faculty_add_course.html')
    else:
        return redirect("../login")

@csrf_exempt
def faculty_add_exam(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0):
        if(request.POST.get('exam_name', False) != False and request.POST.get('description', False) != False and request.POST.get('course_id', False) != False and request.POST.get('year', False) != False and request.POST.get('status', False) != False and request.POST.get('startDate', False) != False and request.POST.get('endDate', False) != False and request.POST.get('startTime', False) != False and request.POST.get('endTime', False) != False and request.POST.get('pass_percentage', False) != False and request.POST.get('no_of_questions', False) != False and request.POST.get('attempts_allowed', False) != False):
            temp = exam_detail()
            temp.exam_name = request.POST['exam_name']
            temp.description = request.POST['description']
            temp.course_id = course.objects.get(id=request.POST['course_id'])
            temp.year = request.POST['year']
            temp.status = request.POST['status']
            temp.start_time = request.POST['startDate']+" "+request.POST['startTime']
            temp.end_time = request.POST['endDate']+" "+request.POST['endTime']
            temp.pass_percentage = request.POST['pass_percentage']
            temp.no_of_questions = request.POST['no_of_questions']
            temp.attempts_allowed = request.POST['attempts_allowed']
            if(exam_detail.objects.filter(exam_name=temp.exam_name, course_id = temp.course_id, year = temp.year).count() == 0):
                temp.save()
                print("saved")
                message = "Examination was successfully added!"
                return render(request ,'online_exam/faculty_add_exam.html', {"message":message})
            else:
                wrong_message = "Sorry, exam already exists!"
                return render(request ,'online_exam/faculty_add_exam.html', {"wrong_message":wrong_message})
        else:
            print("else entered")
            return render(request ,'online_exam/faculty_add_exam.html', {"courses":course.objects.all()})
    else:
        return redirect("../login")

def faculty_add_topic(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0):
        if(request.POST.get('topic_name', False) != False and request.POST.get('status', False) != False and request.POST.get('description', False) != False):
            temp = topic()
            temp.topic_name = request.POST['topic_name']
            temp.description = request.POST['description']
            temp.status = request.POST['status']
            if(topic.objects.filter(topic_name=temp.topic_name).count() == 0):
                temp.save()
                message = "Topic was successfully added!!"
                return render(request ,'online_exam/faculty_add_topic.html', {"message":message})
            else:
                wrong_message = "Sorry, topic already exists!!"
                return render(request ,'online_exam/faculty_add_topic.html', {"wrong_message":wrong_message})
        else:
            return render(request ,'online_exam/faculty_add_topic.html')
    else:
        return redirect("../login")

def faculty_add_subtopic(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0):
        if(request.POST.get('subtopic_name', False) != False and request.POST.get('status', False) != False and request.POST.get('description', False) != False and request.POST.get('topic_id', False) != False):
            temp = subtopic()
            temp.subtopic_name = request.POST['subtopic_name']
            temp.description = request.POST['description']
            temp.status = request.POST['status']
            temp.topic_id = topic.objects.get(id=request.POST['topic_id'])
            if(subtopic.objects.filter(subtopic_name=temp.subtopic_name).count() == 0):
                temp.save()
                message = "Subtopic was successfully added!!"
                return render(request ,'online_exam/faculty_add_subtopic.html',  {"topics":topic.objects.all(),"message":message})
            else:
                wrong_message = "Sorry, subtopic already exists!!"
                return render(request ,'online_exam/faculty_add_subtopic.html',  {"topics":topic.objects.all(),"wrong_message":wrong_message})
        else:
            return render(request ,'online_exam/faculty_add_subtopic.html', {"topics":topic.objects.all()})
    else:
        return redirect("../login")
def faculty_add_question(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0):
        """print(request.POST.get("question", False))
        print(request.POST.get("description", False))
        print(request.POST.get("question_type", False))
        print(request.POST.get("subtopic", False))
        print(request.POST.get("level", False))
        print(request.POST.get("exam", False))
        print(request.POST.get("score", False))
        print(request.POST.get("status", False))"""
        if(request.method == "POST" and request.POST.get("question", False) != False and request.POST.get("description", False) != False and request.POST.get("question_type", False) != False and request.POST.get("subtopic", False) != False and request.POST.get("level", False) != False and request.POST.get("exam", False) != False and request.POST.get("score", False) != False and request.POST.get("status", False) != False):
            temp = question_bank()
            temp.question =request.POST["question"] 
            temp.description = request.POST["description"]
            temp.question_type = question_type.objects.get(pk=request.POST["question_type"])
            temp.subtopic_id = subtopic.objects.get(pk = request.POST["subtopic"])
            temp.level_id = level.objects.get(pk =request.POST["level"])
            temp.exam_id = exam_detail.objects.get(pk =request.POST["exam"])
            temp.score = request.POST["score"]
            temp.status = request.POST["status"]
            if(question_bank.objects.filter(question = temp.question, subtopic_id = temp.subtopic_id).exists() == False):
                temp.save()
                question_id = question_bank.objects.get(question = temp.question, subtopic_id = temp.subtopic_id)
                #print(temp)
                #print(temp.question_type.q_type)
                if(temp.question_type.q_type == "Multiple Choice Single Answer" or temp.question_type.q_type == "Multiple Choice Multiple Answer"):
                    for i in range(1, int(request.POST["options_number"])+1):
                        new_option = option()
                        new_option.question_id = question_id
                        new_option.option_no = i
                        new_option.option_value = request.POST["option"+str(i)]
                        new_option.save()
                    if(temp.question_type.q_type == "Multiple Choice Single Answer"):
                        temp_answer = answer()
                        temp_answer.question_id = question_id
                        temp_answer.answer = request.POST['options']
                        temp_answer.save()
                    elif(temp.question_type.q_type == "Multiple Choice Multiple Answer"):
                        answers = request.POST.getlist('options[]')
                        for i in answers:
                            new_answer = answer()
                            new_answer.question_id = question_id
                            new_answer.answer = i
                            new_answer.save()
                elif(temp.question_type.q_type == "Match the Column"):
                    for i in range(1, int(request.POST["questions_number"])+1):
                        new_row = MatchTheColumns()
                        new_row.question_id = question_id
                        new_row.question = request.POST["matchQues" + str(i)]
                        new_row.answer = request.POST["matchAns" + str(i)]
                        new_row.save()
                else:
                    temp_answer = answer()
                    temp_answer.question_id = question_id
                    temp_answer.answer = request.POST['answer']
                    temp_answer.save()
                message = "Question was successfully created!!"
                return render(request ,'online_exam/faculty_add_question.html',  {"courses": course.objects.all(), "topics": topic.objects.all(), "levels": level.objects.all(), "question_type":question_type.objects.all(), "message":message})
            else:
                wrong_message = "Sorry, question already exists under the subtopic!!"
                return render(request ,'online_exam/faculty_add_question.html', {"courses": course.objects.all(), "topics": topic.objects.all(), "levels": level.objects.all(), "question_type":question_type.objects.all(), "wrong_message":wrong_message})   
        else:
            return render(request ,'online_exam/faculty_add_question.html', {"courses": course.objects.all(), "topics": topic.objects.all(), "levels": level.objects.all(), "question_type":question_type.objects.all()})
    else:
        return redirect("../login")

@csrf_exempt
def faculty_modify_course(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0):
        if request.method=="POST":
            temp = course()
            temp.course_id = request.POST['id']
            temp.course_name = request.POST['course_name']
            temp.description = request.POST['description']
            temp.faculty = request.POST['faculty']
            temp.status = request.POST['status']
            if(course.objects.filter(course_name=temp.course_name).count() == 0 ):
                course.objects.filter(id=temp.course_id).update(course_name=temp.course_name, description = temp.description, status = temp.status, modified = datetime.datetime.now())
                message = "Course was updated successfully!!"
                return render(request ,'online_exam/faculty_modify_course.html', {"courses":course.objects.all(),"message":message})
            elif(course.objects.filter(course_name = temp.course_name).count() == 1 and list(course.objects.filter(course_name=temp.course_name).values("id"))[0]['id'] == int(request.POST['id'])):
                course.objects.filter(id=temp.course_id).update(course_name=temp.course_name, description = temp.description, faculty=temp.faculty, status = temp.status, modified = datetime.datetime.now())
                message = "Course was updated successfully!!"
                return render(request ,'online_exam/faculty_modify_course.html', {"courses":course.objects.all(),"message":message})
            else:
                wrong_message = "Sorry, the course already exists!!"
                return render(request ,'online_exam/faculty_modify_course.html', {"courses":course.objects.all(),"wrong_message":wrong_message})
        else:
            return render(request ,'online_exam/faculty_modify_course.html', {"courses":course.objects.all()})
    else:
        return redirect("../login")

@csrf_exempt
def faculty_modify_exam(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0):
        print("entered")
        print("id---------------------------------------------------------", request.POST.get('id'))
        if(request.POST.get('id', False) != False and request.POST.get('exam_name', False) != False and request.POST.get('exam_name', False) != False and request.POST.get('description', False) != False and request.POST.get('course_id', False) != False and request.POST.get('year', False) != False and request.POST.get('status', False) != False and request.POST.get('startDate', False) != False and request.POST.get('endDate', False) != False and request.POST.get('startTime', False) != False and request.POST.get('endTime', False) != False and request.POST.get('pass_percentage', False) != False and request.POST.get('no_of_questions', False) != False and request.POST.get('attempts_allowed', False) != False):
            #if request.method == 'POST':
            temp = exam_detail()
            print("if entered")
            temp.id = request.POST['id']
            temp.exam_name = request.POST['exam_name']
            temp.description = request.POST['description']
            temp.course_id = course.objects.get(pk=request.POST['course_id'])
            temp.year = request.POST['year']
            temp.status = request.POST['status']
            temp.start_time = request.POST['startDate']+" "+request.POST['startTime']
            temp.end_time = request.POST['endDate']+" "+request.POST['endTime']
            temp.pass_percentage = request.POST['pass_percentage']
            temp.no_of_questions = request.POST['no_of_questions']
            temp.attempts_allowed = request.POST['attempts_allowed']
            if(exam_detail.objects.filter(exam_name=temp.exam_name, course_id = temp.course_id, year = temp.year).count() == 0):
                exam_detail.objects.filter(id=temp.id).update(exam_name=temp.exam_name, description=temp.description, course_id=temp.course_id, year=temp.year, status=temp.status, start_time=temp.start_time, end_time=temp.end_time, pass_percentage=temp.pass_percentage, no_of_questions=temp.no_of_questions, attempts_allowed=temp.attempts_allowed, modified=datetime.datetime.now())
                message = "Examination was successfully updated!"
                return render(request ,'online_exam/faculty_modify_exam.html', {"message":message, "exams": exam_detail.objects.all()})
            elif(exam_detail.objects.filter(exam_name=temp.exam_name, course_id = temp.course_id, year = temp.year).count() == 1 and list(exam_detail.objects.filter(exam_name=temp.exam_name, course_id = temp.course_id, year = temp.year).values("id"))[0]['id'] == int(request.POST['id'])):
                exam_detail.objects.filter(id=temp.id).update(exam_name=temp.exam_name, description=temp.description, course_id=temp.course_id, year=temp.year, status=temp.status, start_time=temp.start_time, end_time=temp.end_time, pass_percentage=temp.pass_percentage, no_of_questions=temp.no_of_questions, attempts_allowed=temp.attempts_allowed, modified=datetime.datetime.now())
                message = "Examination was successfully updated!"
                return render(request ,'online_exam/faculty_modify_exam.html', {"message":message, "exams": exam_detail.objects.all()})
            else:
                wrong_message = "Sorry, exam already exists!"
                return render(request ,'online_exam/faculty_modify_exam.html', {"wrong_message":wrong_message, "exams": exam_detail.objects.all()})
        else:
            print("else entered")
            return render(request ,'online_exam/faculty_modify_exam.html', {"exams":exam_detail.objects.all()})
    else:
        return redirect("../login")
def faculty_modify_topic(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0):
        if(request.POST.get('id', False) != False and request.POST.get('topic_name', False) != False and request.POST.get('status', False) != False and request.POST.get('description', False) != False):
            temp = topic()
            temp.topic_id = request.POST['id']
            temp.topic_name = request.POST['topic_name']
            temp.description = request.POST['description']
            temp.status = request.POST['status']
            if(topic.objects.filter(topic_name=temp.topic_name).count() == 0 ):
                topic.objects.filter(id=temp.topic_id).update(topic_name=temp.topic_name, description = temp.description, status = temp.status, modified = datetime.datetime.now())
                message = "Topic was updated successfully!!"
                return render(request ,'online_exam/faculty_modify_topic.html', {"topics":topic.objects.all(),"message":message})
            elif(topic.objects.filter(topic_name = temp.topic_name).count() == 1 and list(topic.objects.filter(topic_name=temp.topic_name).values("id"))[0]['id'] == int(request.POST['id'])):
                topic.objects.filter(id=temp.topic_id).update(topic_name=temp.topic_name, description = temp.description, status = temp.status, modified = datetime.datetime.now())
                message = "Topic was updated successfully!!"
                return render(request ,'online_exam/faculty_modify_topic.html', {"topics":topic.objects.all(),"message":message})
            else:
                wrong_message = "Sorry, the topic already exists!!"
                return render(request ,'online_exam/faculty_modify_topic.html', {"topics":topic.objects.all(),"wrong_message":wrong_message})
        else:
            return render(request ,'online_exam/faculty_modify_topic.html', {"topics":topic.objects.all()})
    else:
        return redirect("../login")

def faculty_modify_subtopic(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0):
        if(request.POST.get('id', False) != False and request.POST.get('subtopic_name', False) != False and request.POST.get('status', False) != False and request.POST.get('description', False) != False and request.POST.get('topic_id', False) != False):
            temp = subtopic()
            temp.subtopic_id = request.POST['id']
            temp.subtopic_name = request.POST['subtopic_name']
            temp.description = request.POST['description']
            temp.status = request.POST['status']
            temp.topic_id = topic.objects.get(id=request.POST['topic_id'])
            if(subtopic.objects.filter(subtopic_name=temp.subtopic_name, topic_id = temp.topic_id).count() == 0 ):
                subtopic.objects.filter(id=temp.subtopic_id).update(subtopic_name=temp.subtopic_name, description = temp.description, topic_id =temp.topic_id, status = temp.status, modified = datetime.datetime.now())
                message = "SubTopic was updated successfully!!"
                return render(request ,'online_exam/faculty_modify_subtopic.html', {"subtopics":subtopic.objects.all(),"topics":topic.objects.all(),"message":message})
            elif(subtopic.objects.filter(subtopic_name=temp.subtopic_name, topic_id = temp.topic_id).count() == 1 and list(subtopic.objects.filter(subtopic_name=temp.subtopic_name, topic_id = temp.topic_id).values("id"))[0]['id'] == int(request.POST['id'])):
                subtopic.objects.filter(id=temp.subtopic_id).update(subtopic_name=temp.subtopic_name, description = temp.description, topic_id =temp.topic_id, status = temp.status, modified = datetime.datetime.now())
                message = "SubTopic was updated successfully!!"
                return render(request ,'online_exam/faculty_modify_subtopic.html', {"subtopics":subtopic.objects.all(),"topics":topic.objects.all(),"message":message})
            else:
                wrong_message = "Sorry, the subtopic already exists!!"
                return render(request ,'online_exam/faculty_modify_subtopic.html', {"subtopics":subtopic.objects.all(),"topics":topic.objects.all(),"wrong_message":wrong_message})
        else:
            return render(request ,'online_exam/faculty_modify_subtopic.html', {"subtopics":subtopic.objects.all(),"topics":topic.objects.all()})
    else:
        return redirect("../login")

def faculty_modify_question(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0):
        Final = dict()
        if(request.method == "POST" and request.POST.get("id", False) != False and request.POST.get("question", False) != False and request.POST.get("description", False) != False and request.POST.get("question_type", False) != False and request.POST.get("subtopic", False) != False and request.POST.get("level", False) != False and request.POST.get("exam", False) != False and request.POST.get("score", False) != False and request.POST.get("status", False) != False):
            temp = question_bank()
            id = request.POST["id"]
            temp.question =request.POST["question"] 
            temp.description = request.POST["description"]
            temp.question_type = question_type.objects.get(pk=request.POST["question_type"])
            temp.subtopic_id = subtopic.objects.get(pk = request.POST["subtopic"])
            temp.level_id = level.objects.get(pk =request.POST["level"])
            temp.exam_id = exam_detail.objects.get(pk =request.POST["exam"])
            temp.score = request.POST["score"]
            temp.status = request.POST["status"]
            if(question_bank.objects.filter(question = temp.question, subtopic_id = temp.subtopic_id).exists() == False or (question_bank.objects.filter(question = temp.question, subtopic_id = temp.subtopic_id).count() == 1 and question_bank.objects.get(question = temp.question, subtopic_id = temp.subtopic_id).id == int(request.POST['id']))):
                question_bank.objects.filter(pk = int(request.POST["id"])).update(question = temp.question, description = temp.description, question_type = temp.question_type, subtopic_id = temp.subtopic_id, level_id = temp.level_id, exam_id = temp.exam_id, score = temp.score, status = temp.status, modified = datetime.datetime.now())
                question_id = question_bank.objects.get(id = int(request.POST["id"]))
                if(temp.question_type.q_type == "Multiple Choice Single Answer" or temp.question_type.q_type == "Multiple Choice Multiple Answer"):
                    option.objects.filter(question_id=question_id).delete()
                    answer.objects.filter(question_id=question_id).delete()
                    for i in range(1, int(request.POST["options_number"])+1):
                        new_option = option()
                        new_option.question_id = question_id
                        new_option.option_no = i
                        new_option.option_value = request.POST["option"+str(i)]
                        new_option.save()
                    if(temp.question_type.q_type == "Multiple Choice Single Answer"):
                        temp_answer = answer()
                        temp_answer.question_id = question_id
                        temp_answer.answer = request.POST['options']
                        temp_answer.save()
                    elif(temp.question_type.q_type == "Multiple Choice Multiple Answer"):
                        answers = request.POST.getlist('options[]')
                        for i in answers:
                            new_answer = answer()
                            new_answer.question_id = question_id
                            new_answer.answer = i
                            new_answer.save()
                elif(temp.question_type.q_type == "Match the Column"):
                    MatchTheColumns.objects.filter(question_id=question_id).delete()
                    for i in range(1, int(request.POST["questions_number"])+1):
                        new_row = MatchTheColumns()
                        new_row.question_id = question_id
                        new_row.question = request.POST["matchQues" + str(i)]
                        new_row.answer = request.POST["matchAns" + str(i)]
                        new_row.save()
                else:
                    answer.objects.filter(question_id = question_id).update(answer = request.POST['answer'])
                message = "Question was successfully modified!!"
                Final = {"message":message}
            else:
                wrong_message = "Sorry, question already exists under the subtopic!!"
                Final = {"wrong_message":wrong_message}
        V=[]
        for i in question_bank.objects.all():
            A = dict()
            A['id'] = i.id
            A['question'] = i.question
            A['description'] = i.description
            A['question_type'] = i.question_type.q_type
            A['subtopic'] = i.subtopic_id.subtopic_name
            if(A['question_type']  == "Multiple Choice Single Answer" or A['question_type'] == "Multiple Choice Multiple Answer"):
                options = ""
                for j in option.objects.filter(question_id = i).all():
                    options += (j.option_value + "; ")
                A['options'] = options
                answers = ""
                for j in answer.objects.filter(question_id = i).all():
                    answers += (option.objects.get(question_id = i, option_no=j.answer).option_value + "; ")
                A['answers'] = answers
            elif(A['question_type'] == "Match the Column"):
                A['options'] = "None"
                A['answers'] = ""
                for j in MatchTheColumns.objects.filter(question_id = i).all():
                    A['answers'] += j.question + " - " + j.answer + "; "
            else:
                A['options'] = "None"
                solution = answer.objects.get(question_id = i)
                A['answers'] = solution.answer
            A['level'] = i.level_id.level_name
            A['exam'] = i.exam_id.exam_name
            A['score'] = i.score
            A['created'] = i.created
            A['modified'] = i.modified
            A['status'] = i.status
            A['topic_name'] = (i.subtopic_id.topic_id.topic_name)
            V.append(A)
            Final["questions"] = V
        return render(request ,'online_exam/faculty_modify_question.html', Final)
    else:
        return redirect("../login")

@csrf_exempt
def faculty_update_course(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0):
        if request.method=="POST":
            ID = request.POST['id']
            print(ID)
            data = course.objects.get(pk = int(request.POST['id']))
            return render(request ,'online_exam/faculty_update_course.html', {"data": data})
    else:
        return redirect("../login")

@csrf_exempt
def faculty_update_exam(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0):
        result = exam_detail.objects.get(pk= int(request.POST['id']))
        start_date = ((str(result.start_time).split())[0])
        end_date = ((str(result.end_time).split())[0])
        start_time = ((str(result.start_time).split())[1]).split("+")[0]
        end_time = ((str(result.end_time).split())[1]).split("+")[0]
        return render(request ,'online_exam/faculty_update_exam.html', {"result": result, "courses": course.objects.all(), "start_date":start_date, "end_date":end_date, "start_time":start_time, "end_time":end_time})
        #print("id---------------------------------------------------------", int(request.POST['id']))
    else:
        return redirect("../login")

def faculty_update_topic(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0):
        result = topic.objects.get(pk = int(request.POST['id']))
        return render(request ,'online_exam/faculty_update_topic.html', {"result": result})
    else:
        return redirect("../login")

def faculty_update_subtopic(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0):
        result = subtopic.objects.get(pk = int(request.POST['id']))
        print(result.topic_id.topic_name)
        return render(request ,'online_exam/faculty_update_subtopic.html', {"result":result, "topics":topic.objects.all()})
    else:
        return redirect("../login")

def faculty_update_question(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0):
        if(request.method == "POST" and request.POST.get('id', False) != False):
            query = question_bank.objects.get(pk = int(request.POST['id']))
            ques = dict()
            ques['id'] = query.id
            ques['question'] = query.question
            ques['description'] = query.description
            ques['question_type'] = query.question_type.q_type
            ques['subtopic'] = query.subtopic_id.id
            ques['topic'] = query.subtopic_id.topic_id.id
            ques['numbers'] = range(2, 11)
            if(ques['question_type']  == "Multiple Choice Single Answer" or ques['question_type'] == "Multiple Choice Multiple Answer"):
                ques['options'] = []
                for i in option.objects.filter(question_id = query).all():
                    if answer.objects.filter(question_id = query, answer = i.option_no).count() == 1:
                        ques['options'].append({"option_desig":chr(i.option_no+96), "option_no":i.option_no, "option_value":i.option_value, "answer": 1})
                    elif answer.objects.filter(question_id = query, answer = i.option_no).count() == 0:
                        ques['options'].append({"option_desig":chr(i.option_no+96), "option_no":i.option_no, "option_value":i.option_value, "answer": 0})               
                ques['options_number'] = option.objects.filter(question_id = query).count()
            elif(ques['question_type'] == "Match the Column"):
                ques['answers'] = []
                j = 1
                for i in MatchTheColumns.objects.filter(question_id = query).all():
                    ques['answers'].append({"ques_no": chr(96+j), "ques_value":i.question, "ans_no": j, "ans_value":i.answer})
                    j += 1
                ques['questions_number'] = MatchTheColumns.objects.filter(question_id = query).count()
            else:
                solution = answer.objects.get(question_id = query)
                ques['answers'] = solution.answer
            ques['level'] = query.level_id.id
            ques['exam'] = query.exam_id.id
            ques['course'] = query.exam_id.course_id.id
            ques['score'] = query.score
            ques['created'] = query.created
            ques['modified'] = query.modified
            ques['status'] = query.status
            ques['courses'] = course.objects.all()
            ques['exams'] = exam_detail.objects.filter(course_id=query.exam_id.course_id).all()
            ques['subtopics'] = subtopic.objects.filter(topic_id=query.subtopic_id.topic_id).all()
            ques['topics'] = topic.objects.all()
            ques['question_types'] = question_type.objects.all()
            ques['levels'] = level.objects.all()
        return render(request ,'online_exam/faculty_update_question.html', ques)
    else:
        return redirect("../login")

def faculty_view_courses(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0):
        return render(request ,'online_exam/faculty_view_courses.html', {"courses":course.objects.all()})
    else:
        return redirect("../login")

@csrf_exempt
def faculty_view_exams(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0):
        data = exam_detail.objects.all()
        #print(data)
        return render(request ,'online_exam/faculty_view_exams.html', {"exams":exam_detail.objects.all()})
    else:
        return redirect("../login")

def faculty_view_topics(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0):
        return render(request ,'online_exam/faculty_view_topics.html', {"topics":topic.objects.all()})
    else:
        return redirect("../login")

def faculty_view_subtopics(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0):
        L=[]
        for i in subtopic.objects.all():
            K = dict()
            K['subtopic_name'] = i.subtopic_name
            K['description'] = i.description
            K['created'] = i.created
            K['modified'] = i.modified
            K['status'] = i.status
            K['topic_name'] = ((i.topic_id).topic_name)
            L.append(K)
        return render(request ,'online_exam/faculty_view_subtopics.html', {"subtopics":L})
    else:
        return redirect("../login")

def faculty_view_questions(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0):
        V=[]
        for i in question_bank.objects.all():
            A = dict()
            A['question'] = i.question
            A['description'] = i.description
            A['question_type'] = i.question_type.q_type
            A['subtopic'] = i.subtopic_id.subtopic_name
            if(A['question_type']  == "Multiple Choice Single Answer" or A['question_type'] == "Multiple Choice Multiple Answer"):
                options = ""
                for j in option.objects.filter(question_id = i).all():
                    options += (j.option_value + "; ")
                A['options'] = options
                answers = ""
                for j in answer.objects.filter(question_id = i).all():
                    answers += (option.objects.get(question_id = i, option_no=j.answer).option_value + "; ")
                A['answers'] = answers
            elif(A['question_type'] == "Match the Column"):
                A['options'] = "None"
                A['answers'] = ""
                for j in MatchTheColumns.objects.filter(question_id = i).all():
                    A['answers'] += j.question + " - " + j.answer + "; "
            else:
                A['options'] = "None" 
                A['answers'] = answer.objects.get(question_id = i).answer
            A['level'] = i.level_id.level_name
            A['exam'] = i.exam_id.exam_name
            A['score'] = i.score
            A['created'] = i.created
            A['modified'] = i.modified
            A['status'] = i.status
            A['topic_name'] = (i.subtopic_id.topic_id.topic_name)
            V.append(A)
        return render(request ,'online_exam/faculty_view_questions.html',{"questions":V})
    else:
        return redirect("../login")

def faculty_evaluate(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0):
        temp = exam_detail.objects.all()
        data=[]
        for t in temp:
            data1={}
            data1['exam_id'] = t.id
            data1['exam_name']=t.exam_name
            data1['course'] = t.course_id.course_name
            data1['year'] = t.year
            data1['description']=t.description
            data1['no_of_questions']=t.no_of_questions
            data1['pass_percentage']=t.pass_percentage
            data1['duration']=t.end_time - t.start_time
            data.append(data1)
        return render(request ,'online_exam/faculty_evaluate.html', {"data":data})
    else:
        return redirect("../login")

def faculty_exam_registrations(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0):
        if request.method=='POST':
            temp=registration.objects.get(pk=request.POST['user_exam_attempt_id'])
            temp.registered=1-temp.registered
            temp.save()
            return HttpResponse(temp.registered)
        temp=registration.objects.all()
        data=[]
        for i in temp:
            data1={}
            data1['first_name']=(i.user_id).first_name
            data1['last_name']=(i.user_id).last_name
            data1['email']=(i.user_id).email
            data1['phone']=(i.user_id).phone
            data1['exam_name']=(i.exam_id).exam_name
            data1['attempt_no']=i.attempt_no
            data1['registered']=i.registered
            data1['registered_time']=i.registered_time
            data1['exam_id']=i.id;
            data.append(data1)
        return render(request ,'online_exam/faculty_exam_registrations.html',{"data":data})
    else:
        return redirect("../login")


@csrf_exempt
def modify_user(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0):
        if(request.method=='POST'):
            if(request.POST.get('user_id', False) != False and request.POST.get('first_name', False) == False and request.POST.get('password', False) == False): 
                temp=user.objects.get(pk=int(request.POST['user_id']))
                currentUser = user()
                currentUser.first_name = temp.first_name
                currentUser.last_name = temp.last_name
                currentUser.phone = temp.phone
                currentUser.email = temp.email
                currentUser.account_type = temp.account_type
                currentUser.id = temp.id
                return render(request ,'online_exam/modify_user.html', {"currentUser" : currentUser})
            if(request.POST.get('user_id', False) != False and request.POST.get('password', False) != False):
                user.objects.filter(pk=request.POST['user_id']).update(password=make_password(request.POST['password']))
                message = "Password Updated Successfully!!!"
                return render(request ,'online_exam/modify_user.html', {"currentUser" : user.objects.get(pk=request.POST['user_id']), "message":message})
            if(user.objects.filter(email = request.POST['email']).count() == 1 and user.objects.filter(email = request.POST['email'], id = request.POST['user_id']).count() == 1):
                user.objects.filter(pk=request.POST['user_id']).update(first_name=request.POST['first_name'],last_name=request.POST['last_name'],email=request.POST['email'], phone=request.POST['phone'], account_type=request.POST['account_type'])
                message = "Profile Updated Successfully!!!"
                return render(request ,'online_exam/modify_user.html', {"currentUser" : user.objects.get(pk=request.POST['user_id']), "message":message})
            elif(user.objects.filter(email = request.POST['email']).count() == 0):
                user.objects.filter(pk=request.POST['user_id']).update(first_name=request.POST['first_name'],last_name=request.POST['last_name'],email=request.POST['email'], phone=request.POST['phone'], account_type=request.POST['account_type'])
                message = "Profile Updated Successfully!!!"
                return render(request ,'online_exam/modify_user.html', {"currentUser" : user.objects.get(pk=request.POST['user_id']), "message":message})
            else:
                wrong_message = "Sorry email id already exists!!!"
                return render(request ,'online_exam/modify_user.html', {"currentUser" : user.objects.get(pk=request.POST['user_id']), "wrong_message":wrong_message})
        else:
            return redirect("../faculty_user_registrations")
    else:
        return redirect("../login")

@csrf_exempt
def faculty_user_registrations(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0):
        if request.method=="POST":
            temp = user()
            temp.first_name = request.POST['first_name']
            temp.last_name = request.POST['last_name']
            temp.phone = request.POST['phone']
            temp.email = request.POST['email']
            temp.password = make_password(request.POST['password'])
            temp.account_type = request.POST['account_type']
            print(temp)
            if(user.objects.filter(email = temp.email).count() == 0):
                temp.save()
                message = "User was successfully added!!"
                return render(request ,'online_exam/faculty_user_registrations.html',{"message":message, "data":user.objects.all()})
            else:
                wrong_message = "Sorry, user already exists!!"
                return render(request,'online_exam/faculty_user_registrations.html',{"wrong_message":wrong_message, "data":user.objects.all()})
        else:
            return render(request,'online_exam/faculty_user_registrations.html', {"data":user.objects.all()})
    else:
        return redirect("../login")

def faculty_register_evaluate(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0):
        if(request.method == "POST" and request.POST.get("registration_id", False) != False):
            ans = registration.objects.get(pk = int(request.POST["registration_id"])).view_answers
            ans = 1 - int(ans)
            registration.objects.filter(pk = int(request.POST["registration_id"])).update(view_answers = ans)
            return HttpResponse(ans)
        query = []
        for i in registration.objects.filter(exam_id = exam_detail.objects.get(pk = request.POST["exam_id"]), answered = 1).all():
            subquery = dict()
            subquery["first_name"] = i.user_id.first_name
            subquery["last_name"] = i.user_id.last_name
            subquery["attempt_no"] = i.attempt_no
            subquery["course"] = i.exam_id.course_id.course_name
            subquery["year"] = i.exam_id.year
            subquery["exam_id"] = i.exam_id.id
            subquery["id"] = i.id
            if(result.objects.filter(registration_id = i).count() == result.objects.filter(registration_id = i, verify = 1).count()):
                subquery["verify"] = 1
            else:
                subquery["verify"] = 0
            subquery["view_answers"] = i.view_answers
            subquery["score"] = result.objects.filter(registration_id = i).aggregate(Sum('score'))
            if(subquery["score"]["score__sum"] == None):
                subquery["score"] = 0
            else:
                subquery["score"] = int(subquery["score"]["score__sum"])
            query.append(subquery)
        return render(request ,'online_exam/faculty_register_evaluate.html', {"registrations": query})
    else:
        return redirect("../login")

def faculty_manual_evaluate(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0):
        if request.method == "POST":
            if request.POST.get('result_id', False) != False and request.POST.get('check', False) != False and request.POST.get('score', False) != False: 
                if(int(request.POST['check']) == 1):
                    result.objects.filter(pk = int(request.POST['result_id'])).update(score = int(request.POST['score']), verify = 1)
                elif(int(request.POST['check']) == 0):
                    result.objects.filter(pk = int(request.POST['result_id'])).update(score = 0, verify = 1)
                data = dict()
                z = 1
                for i in result.objects.filter(registration_id = registration.objects.get(pk = request.POST["user_exam_attempt_id"])).all():
                    subdata = dict()
                    subdata['question_id'] = i.question_id.id
                    subdata['question'] = i.question_id.question
                    subdata['question_type'] = i.question_id.question_type.q_type
                    if(i.question_id.question_type.id == 1 or i.question_id.question_type.id == 2):
                        opt_dict = dict()
                        for k in option.objects.filter(question_id = i.question_id.id):
                            opt_dict[k.option_no] = k.option_value
                        subdata['options'] = opt_dict
                    else:
                        subdata['options'] = ""
                    subdata["result_id"] = i.id
                    if(subdata['question_type']  == "Multiple Choice Single Answer" or subdata['question_type'] == "Multiple Choice Multiple Answer"):
                        answers = ""
                        for j in answer.objects.filter(question_id = i.question_id).all():
                            answers += (option.objects.get(question_id = i.question_id, option_no=j.answer).option_value + "; ")
                        subdata['answer'] = answers
                    elif(subdata['question_type'] == "Match the Column"):
                        subdata['answer'] = ""
                        for j in MatchTheColumns.objects.filter(question_id = i.question_id).all():
                            subdata['answer'] += j.question + " - " + j.answer + "; "
                    else: 
                        subdata['answer'] = answer.objects.get(question_id = i.question_id).answer
                    subdata['level'] = i.question_id.level_id.level_name
                    subdata['score'] = i.question_id.score
                    subdata['gained_score'] = i.score
                    subdata['your_answers'] = i.answer
                    subdata['verify'] = i.verify
                    data[z] = subdata
                    z += 1
                data = json.dumps(data)
                return HttpResponse(data)
            data = dict()
            z = 1
            for i in result.objects.filter(registration_id = registration.objects.get(pk = int(request.POST['registration_id']))).all():
                subdata = dict()
                subdata['question_id'] = i.question_id.id
                subdata['question'] = i.question_id.question
                subdata['question_type'] = i.question_id.question_type.q_type
                if(i.question_id.question_type.id == 1 or i.question_id.question_type.id == 2):
                    opt_dict = dict()
                    for k in option.objects.filter(question_id = i.question_id.id):
                        opt_dict[k.option_no] = k.option_value
                    subdata['options'] = opt_dict
                else:
                    subdata['options'] = ""
                subdata["result_id"] = i.id
                if(subdata['question_type']  == "Multiple Choice Single Answer" or subdata['question_type'] == "Multiple Choice Multiple Answer"):
                    answers = ""
                    for j in answer.objects.filter(question_id = i.question_id).all():
                        answers += (option.objects.get(question_id = i.question_id, option_no=j.answer).option_value + "; ")
                    subdata['answer'] = answers
                elif(subdata['question_type'] == "Match the Column"):
                    subdata['answer'] = ""
                    for j in MatchTheColumns.objects.filter(question_id = i.question_id).all():
                        subdata['answer'] += j.question + " - " + j.answer + "; "
                else: 
                    subdata['answer'] = answer.objects.get(question_id = i.question_id).answer
                subdata['level'] = i.question_id.level_id.level_name
                subdata['score'] = i.question_id.score
                subdata['gained_score'] = i.score
                subdata['your_answers'] = i.answer
                subdata['verify'] = i.verify
                data[z] = subdata
                z += 1
            data = json.dumps(data)
            return render(request ,'online_exam/faculty_manual_evaluate.html', {"data":data, "exam_id":1, "registration_id":1})
    else:
        return redirect("../login")

@csrf_exempt
def faculty_profile(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0):
        if(request.method=='POST'):
            if(request.POST.get('password', False) != False):
                user.objects.filter(pk=request.session['id']).update(password=make_password(request.POST['password']))
                message = "Password Updated Successfully!!!"
                return render(request ,'online_exam/faculty_profile.html', {"currentUser" : user.objects.get(pk=request.session['id']), "message":message})
            if(user.objects.filter(email = request.POST['email']).count() == 1 and user.objects.filter(email = request.POST['email'], id = request.session['id']).count() == 1):
                user.objects.filter(pk=request.session['id']).update(first_name=request.POST['first_name'],last_name=request.POST['last_name'],email=request.POST['email'], phone=request.POST['phone'])
                message = "Profile Updated Successfully!!!"
                return render(request ,'online_exam/faculty_profile.html', {"currentUser" : user.objects.get(pk=request.session['id']), "message":message})
            elif(user.objects.filter(email = request.POST['email']).count() == 0):
                user.objects.filter(pk=request.session['id']).update(first_name=request.POST['first_name'],last_name=request.POST['last_name'],email=request.POST['email'], phone=request.POST['phone'])
                message = "Profile Updated Successfully!!!"
                return render(request ,'online_exam/faculty_profile.html', {"currentUser" : user.objects.get(pk=request.session['id']), "message":message})
            else:
                wrong_message = "Sorry email id already exists!!!"
                return render(request ,'online_exam/faculty_profile.html', {"currentUser" : user.objects.get(pk=request.session['id']), "wrong_message":wrong_message})
        temp=user.objects.get(pk=int(request.session['id']))
        currentUser = user()
        currentUser.first_name = temp.first_name
        currentUser.last_name = temp.last_name
        currentUser.phone = temp.phone
        currentUser.email = temp.email
        currentUser.account_type = temp.account_type
        currentUser.id = temp.id
        return render(request, "online_exam/faculty_profile.html", {"currentUser" : currentUser})
    else:
        return redirect("../login")
# Create your views here.
def student_dashboard(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 1):
        perform = []
        for i in registration.objects.filter(user_id = user.objects.get(id = request.session['id']), answered = 1).all():
            perf = dict()
            perf["exam_name"] = i.exam_id.exam_name
            gained_score = result.objects.filter(registration_id = i.id).aggregate(Sum('score'))
            if(gained_score['score__sum'] == None):
                gained_score = 0
            else:
                gained_score = int(gained_score['score__sum'])
            total_score = 0
            for j in result.objects.filter(registration_id = i.id).all():
                total_score += j.question_id.score
            if(total_score == 0):
                perf["percentage"] = 0
            else:
                perf["percentage"] = gained_score/total_score * 100
            perform.append(perf)
        now = datetime.datetime.now()
        curr = str(now.year) + "-" + str(now.month) + "-01"
        curr_year = int(now.year)
        curr_month = int(now.month)
        dataArray = []
        for i in range(0, 6):
            if(curr_month-i <= 0):
                curr_year -= 1
                curr_month += 12
            curr_array = dict()
            curr_array["year"] = curr_year
            curr_array["month"] = curr_month - i -1
            if(curr_month - i != 12):
                curr_array["count"] = registration.objects.filter(answered = 1, registered_time__range = (datetime.date(curr_year, curr_month-i, 1), datetime.date(curr_year, curr_month-i + 1, 1))).count()
            else:
                curr_array["count"] = registration.objects.filter(answered = 1, registered_time__range = (datetime.date(curr_year, 12, 1), datetime.date(curr_year+1, 1, 1))).count()
            dataArray.append(curr_array)
        pass_p = 0
        count = 0
        for i in registration.objects.filter(answered=1, view_answers = 1, user_id = user.objects.get(pk = request.session["id"])).all():
            gained_score = result.objects.filter(registration_id = i).aggregate(Sum('score'))
            if(gained_score['score__sum'] == None):
                gained_score = 0
            else:
                gained_score = int(gained_score['score__sum'])
            total_score = 0
            for j in result.objects.filter(registration_id = i).all():
                total_score += j.question_id.score
            if(gained_score >= i.exam_id.pass_percentage*total_score/100):
                pass_p += 1
            count += 1
        if(count == 0):
            pass_percentage = 0
        else:
            pass_percentage = pass_p*100/count
        return render(request, 'online_exam/student_dashboard.html', {"number_of_exams":exam_detail.objects.count(), "no_of_users":user.objects.count(), "pass_percentage":pass_percentage, "dataArray":dataArray, "performance":perform})
    else:
        return redirect("../login")

def student_exams(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 1):
        Final = dict()
        if(request.method == "POST" and request.POST.get('exam_id', False) != False):
            temp = registration()
            temp.user_id = user.objects.get(id = request.session['id'])
            temp.exam_id = exam_detail.objects.get(id = int(request.POST['exam_id']))
            temp.attempt_no = registration.objects.filter(user_id = temp.user_id, exam_id = temp.exam_id).count() + 1
            temp.save()
            Final["message"] = "Applied for registration successfully!!"
        exams = []
        for i in exam_detail.objects.filter(status="1").all():
            tmpdct = dict()
            tmpdct["id"] = i.id
            tmpdct["exam_name"] = i.exam_name
            tmpdct["description"] = i.description
            tmpdct["course_name"] = i.course_id.course_name
            tmpdct["year"] = i.year
            user_id = user.objects.get(id = request.session['id'])
            exam_id = i
            tmpdct["attempts_left"] = int(i.attempts_allowed) - registration.objects.filter(user_id = user_id, exam_id = exam_id).count()
            exams.append(tmpdct)
        Final["exams"] = exams
        return render(request, 'online_exam/student_exams.html', Final)
    else:
        return redirect("../login")

def student_attempt_exam(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 1 and request.POST.get('registration_id', False) != False and request.POST.get('exam_id', False) != False):
        questions = question_bank.objects.filter(exam_id = exam_detail.objects.get(id = int(request.POST['exam_id']))).all()
        K = dict()
        registration_id = request.POST['registration_id']
        exam_id = ""
        j = 0
        for i in questions:
            L = dict()
            L['question_id'] = i.id
            L['question'] = i.question
            L['question_type'] = i.question_type.q_type
            if(i.question_type.id == 1 or i.question_type.id == 2):
                opt_dict = dict()
                for k in option.objects.filter(question_id = i.id):
                    opt_dict[k.option_no] = k.option_value
                L['options'] = opt_dict
            else:
                L['options'] = ""
            #L['answer'] = dict(answer.objects.filter(question_id = i.id).values("answer"))
            if(i.question_type.id == 5):
                m = 1
                L['mtcQuestions'] = dict()
                L['mtcAnswers'] = dict()
                for l in MatchTheColumns.objects.filter(question_id = i).all():
                    L['mtcQuestions'][m] = l.question    
                    m += 1
                m = 1
                for l in MatchTheColumns.objects.filter(question_id = i).order_by('?').all():
                    L['mtcAnswers'][m] = l.answer    
                    m += 1
            L['level'] = i.level_id.level_name
            L['subtopic'] = i.subtopic_id.subtopic_name
            L['topic'] = i.subtopic_id.topic_id.topic_name
            L['score'] = i.score
            L['exam'] = i.exam_id.exam_name
            exam_id = i.exam_id.id
            L['course'] = i.exam_id.course_id.course_name
            j += 1
            K[j] = L
        final = json.dumps(K)
        a = datetime.datetime.now()
        b = datetime.datetime(i.exam_id.end_time.year,i.exam_id.end_time.month,i.exam_id.end_time.day,i.exam_id.end_time.hour,i.exam_id.end_time.minute,i.exam_id.end_time.second)
        seconds = math.floor((b-a).total_seconds())
        return render(request, 'online_exam/student_attempt_exam.html', {"myArray":final, "sizeMyArray":j, "exam_id":exam_id, "registration_id":registration_id, "seconds": seconds})
    else:
        return redirect("../login")
def student_approved_exams(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 1):
        Final = []
        for i in registration.objects.filter(user_id = user.objects.get(pk = int(request.session['id'])), registered = 1): 
            exams = dict()
            exams["registration_id"] = i.id
            exams["exam_id"] = i.exam_id.id
            exams["exam_name"] = i.exam_id.exam_name
            exams["start_time"] = i.exam_id.start_time
            exams["end_time"] = i.exam_id.end_time
            exams["course_name"] = i.exam_id.course_id.course_name
            exams["description"] = i.exam_id.description
            exams["attempt_no"] = i.attempt_no
            exams["no_of_questions"] = i.exam_id.no_of_questions
            exams["pass_percentage"] = i.exam_id.pass_percentage
            start_time = i.exam_id.start_time
            end_time = i.exam_id.end_time
            if(start_time <= timezone.now() and end_time >= timezone.now() and i.answered == 0 and i.registered == 1):
                exams["attemptable"] = 1
            else:
                exams["attemptable"] = 0
            Final.append(exams)
        return render(request, 'online_exam/student_approved_exams.html', {"exams":Final, "current_time":datetime.datetime.now()}) 
    else:
        return redirect("../login")

def student_verify(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 1):
        attempted = json.loads(request.POST.get("answer", False))
        registration.objects.filter(id = request.POST["registration_id"]).update(answered = 1)
        marks = 0
        for i in attempted.keys():
            attempted_answer = dict(attempted[i])
            print(attempted_answer['answers'])
            #print(attempted_answer['question_id'])
            ans = dict()
            ques = question_bank.objects.get(pk = attempted_answer['question_id'])
            ques_type = ques.question_type.q_type
            if(ques_type == "Multiple Choice Single Answer" or ques_type == "Multiple Choice Multiple Answer"):
                for j in answer.objects.filter(question_id = ques).all():
                    opt = option.objects.get(question_id = ques, option_no=j.answer)
                    ans[opt.option_no] = opt.option_value
                temp = result()
                temp.registration_id = registration.objects.get(pk = int(request.POST["registration_id"]))
                temp.question_id = ques
                temp.answer = ""
                for j in attempted_answer["answers"].keys():
                    temp.answer += attempted_answer["answers"][j] + "; "
                if(json.dumps(ans) == json.dumps(attempted_answer['answers'])):
                    temp.score = int(attempted_answer['score'])
                else:
                    temp.score = 0
                marks += temp.score
                temp.verify = 1
                temp.save()
            elif(ques_type == "Match the Column"):
                for j in MatchTheColumns.objects.filter(question_id = ques).all():
                    ans[j.question] = j.answer
                temp = result()
                temp.question_id = ques
                temp.registration_id = registration.objects.get(pk = int(request.POST["registration_id"]))
                temp.answer = ""
                for j in attempted_answer["answers"].keys():
                    temp.answer += j + " - " + attempted_answer["answers"][j] + "; "
                if(json.dumps(ans) == json.dumps(attempted_answer['answers'])):
                    temp.score = int(attempted_answer['score'])
                else:
                    temp.score = 0
                marks += temp.score
                temp.verify = 1
                temp.save()
            else:
                temp = result()
                temp.registration_id = registration.objects.get(pk = int(request.POST["registration_id"]))
                temp.question_id = ques
                temp.answer = dict(attempted_answer['answers'])
                temp.answer = temp.answer['1']
                temp.score = 0
                temp.verify = 0
                temp.save()                 
        return HttpResponse(marks)
    else:
        return redirect("../login")

def student_progress(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 1):
        query = []
        for i in registration.objects.filter(user_id = user.objects.get(pk = request.session['id']), answered = 1, view_answers = 1).all():
            subquery = dict()
            subquery["exam_name"] = i.exam_id.exam_name
            subquery["attempt_no"] = i.attempt_no
            subquery["course"] = i.exam_id.course_id.course_name
            subquery["year"] = i.exam_id.year
            subquery["id"] = i.id
            if(result.objects.filter(registration_id = i).count() == result.objects.filter(registration_id = i, verify = 1).count()):
                subquery["verify"] = 1
            else:
                subquery["verify"] = 0
            subquery["view_answers"] = i.view_answers
            subquery["score"] = result.objects.filter(registration_id = i).aggregate(Sum('score'))
            if(subquery["score"] == None):
                subquery["score"] = 0
            else:
                subquery["score"] = int(subquery["score"]["score__sum"])
            query.append(subquery)
        return render(request, 'online_exam/student_progress.html', {"registrations":query})
    else:
        return redirect("../login")

def student_answer_key(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 1):
        data = []
        for i in result.objects.filter(registration_id = registration.objects.get(pk = request.POST['registration_id'])).all():
            subdata = dict()
            subdata['question_id'] = i.question_id.id
            subdata['question'] = i.question_id.question
            subdata['question_type'] = i.question_id.question_type.q_type
            if(i.question_id.question_type.id == 1 or i.question_id.question_type.id == 2):
                options = ""
                for j in option.objects.filter(question_id = i.question_id.id).all():
                    options += (j.option_value + "; ")
                subdata['options'] = options
            else:
                subdata['options'] = "-"
            subdata["result_id"] = i.id
            if(subdata['question_type']  == "Multiple Choice Single Answer" or subdata['question_type'] == "Multiple Choice Multiple Answer"):
                answers = ""
                for j in answer.objects.filter(question_id = i.question_id).all():
                    answers += (option.objects.get(question_id = i.question_id, option_no=j.answer).option_value + "; ")
                subdata['answer'] = answers
            elif(subdata['question_type'] == "Match the Column"):
                subdata['answer'] = ""
                for j in MatchTheColumns.objects.filter(question_id = i.question_id).all():
                    subdata['answer'] += j.question + " - " + j.answer + "; "
            else: 
                subdata['answer'] = answer.objects.get(question_id = i.question_id).answer
            subdata['level'] = i.question_id.level_id.level_name
            subdata['score'] = i.question_id.score
            subdata['gained_score'] = i.score
            subdata['your_answers'] = i.answer
            subdata['verify'] = i.verify
            data.append(subdata)
        return render(request, 'online_exam/student_answer_key.html', {"data":data})
    else:
        return redirect("../login")

def student_profile(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 1):
        if(request.method=='POST'):
            if(request.POST.get('password', False) != False):
                user.objects.filter(pk=request.session['id']).update(password=make_password(request.POST['password']))
                message = "Password Updated Successfully!!!"
                return render(request ,'online_exam/student_profile.html', {"currentUser" : user.objects.get(pk=request.session['id']), "message":message})
            if(user.objects.filter(email = request.POST['email']).count() == 1 and user.objects.filter(email = request.POST['email'], id = request.session['id']).count() == 1):
                user.objects.filter(pk=request.session['id']).update(first_name=request.POST['first_name'],last_name=request.POST['last_name'],email=request.POST['email'], phone=request.POST['phone'])
                message = "Profile Updated Successfully!!!"
                return render(request ,'online_exam/student_profile.html', {"currentUser" : user.objects.get(pk=request.session['id']), "message":message})
            elif(user.objects.filter(email = request.POST['email']).count() == 0):
                user.objects.filter(pk=request.session['id']).update(first_name=request.POST['first_name'],last_name=request.POST['last_name'],email=request.POST['email'], phone=request.POST['phone'])
                message = "Profile Updated Successfully!!!"
                return render(request ,'online_exam/student_profile.html', {"currentUser" : user.objects.get(pk=request.session['id']), "message":message})
            else:
                wrong_message = "Sorry email id already exists!!!"
                return render(request ,'online_exam/student_profile.html', {"currentUser" : user.objects.get(pk=request.session['id']), "wrong_message":wrong_message})
        temp=user.objects.get(pk=int(request.session['id']))
        currentUser = user()
        currentUser.first_name = temp.first_name
        currentUser.last_name = temp.last_name
        currentUser.phone = temp.phone
        currentUser.email = temp.email
        currentUser.account_type = temp.account_type
        currentUser.id = temp.id
        return render(request, 'online_exam/student_profile.html', {"currentUser" : user.objects.get(pk=request.session['id'])})
    else:
        return redirect("../login")

def login(request):
    if(request.session.get('id', False) == False):
        if(request.method == "POST" and request.POST.get('email', False) != False and request.POST.get('password', False) != False):
            if(user.objects.filter(email = request.POST['email']).exists()):
                login_user = user.objects.get(email = request.POST['email'])
                if (check_password(request.POST.get('password', False),login_user.password) == True):
                    request.session['id'] = login_user.id
                    request.session['first_name'] = login_user.first_name
                    request.session['last_name'] = login_user.last_name
                    request.session['email'] = login_user.email
                    request.session['phone'] = login_user.phone
                    request.session['account_type'] = login_user.account_type
                    return redirect('../login')
                else:
                    return render(request, 'online_exam/Login.html', {"message":"Invalid Credentials!!"})
            else:
                return render(request, 'online_exam/Login.html', {"message":"Invalid Credentials!!"})
        return render(request, 'online_exam/Login.html')
    elif(request.session.get('account_type', False) == 0):
        return redirect("../faculty_dashboard")
    elif(request.session.get('account_type', False) == 1):
        return redirect("../student_dashboard")
    return render(request, 'online_exam/Login.html')

def signup(request):
    if(request.method == "POST" and request.POST.get('first_name', False) != False and request.POST.get('last_name', False) != False and request.POST.get('email', False) != False and request.POST.get('phone', False) != False):
        new_user = user(first_name = request.POST['first_name'], last_name = request.POST['last_name'], phone = request.POST['phone'], email = request.POST['email'], password = make_password(request.POST['password']))
        if(user.objects.filter(email=request.POST['email']).exists()):
            error_message = "Email ID already exists!!"
            return render(request, 'online_exam/Signup.html', {"error_message":error_message})
        else:
            new_user.save()
            message = "Account Created Successfully!!"
            return render(request, 'online_exam/Signup.html', {"message":message})
    return render(request, 'online_exam/Signup.html')

def sign_out(request):
    request.session.flush()
    return redirect('../login')

def authenticate(request, token=None):
    clientSecret = "1c616e2f378f9aa90c936b1560e6d0c372fa5e5a54457356f39573955e7e64b445d2f03673a8905088b43c114465020825f48b79e8ce85b0e20e6ad8b736e860"
    Payload = { 'token': token, 'secret': clientSecret }
    k = requests.post("https://serene-wildwood-35121.herokuapp.com/oauth/getDetails", Payload)
    data = json.loads(k.content) 
    print(data['student'][0]['Student_Email'])
    user_email = data['student'][0]['Student_Email']
    if(user.objects.filter(email=user_email).exists() == False):
        new_user = user()
        new_user.first_name = data['student'][0]['Student_First_Name']
        new_user.last_name = data['student'][0]['Student_Last_name']
        new_user.email = data['student'][0]['Student_Email']
        new_user.phone = data['student'][0]['Student_Mobile']
        new_user.password = make_password("iamstudent")
        new_user.save()
    login_user = user.objects.get(email = user_email)
    request.session['id'] = login_user.id
    request.session['first_name'] = login_user.first_name
    request.session['last_name'] = login_user.last_name
    request.session['email'] = login_user.email
    request.session['phone'] = login_user.phone
    request.session['account_type'] = login_user.account_type
    print(data)
    return redirect('login')

def get_exams_by_course(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0 and request.POST.get('course_id', False) != False):
        exams = dict()
        j = 0
        for i in (exam_detail.objects.filter(course_id=course.objects.filter(id = request.POST.get('course_id', False)).all()).values("id", "exam_name")):
            exams[i['id']] = i['exam_name']
            j += 1
        return HttpResponse(json.dumps(exams))
    return HttpResponseNotFound('<h1>Page not found</h1>')

def get_subtopics_by_topic(request):
    if(request.session.get('id', False) != False and request.session.get('account_type', False) == 0 and request.POST.get('topic_id', False) != False):
        subtopics = dict()
        j = 0
        for i in (subtopic.objects.filter(topic_id=topic.objects.filter(id = request.POST.get('topic_id', False)).all()).values("id", "subtopic_name")):
            subtopics[i['id']] = i['subtopic_name']
            j += 1
        return HttpResponse(json.dumps(subtopics))
    return HttpResponseNotFound('<h1>Page not found</h1>')
