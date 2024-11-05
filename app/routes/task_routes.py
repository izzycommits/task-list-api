from flask import Blueprint, abort, make_response, request, Response
from app.models.task import Task
from app.db import db
from datetime import date
from .route_utilities import validate_model
import requests
import os

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@tasks_bp.post("")
def create_task(): 
    request_body = request.get_json()
    try:
        new_task = Task.from_dict(request_body)
    except KeyError:
        response = {"details": "Invalid data"}
        abort(make_response(response, 400))
    db.session.add(new_task)
    db.session.commit()

    response = {"task": new_task.to_dict()}
    return response, 201


@tasks_bp.get("")
def get_all_tasks(): 
    query = db.select(Task)
    
    title_param = request.args.get("title")
    if title_param:
        query = query.where(Task.title.ilike(f"%{title_param}%"))
    
    sort_param = request.args.get("sort")  
    if sort_param == "desc":
        query = query.order_by(Task.title.desc()) 
    else:
        query = query.order_by(Task.title) 

    query=query.order_by(Task.id)
    tasks = db.session.scalars(query)

    tasks_response =[task.to_dict() for task in tasks]

    return tasks_response


@tasks_bp.get("/<task_id>")
def get_single_task(task_id):
    task = validate_model(Task, task_id)
    return {"task":task.to_dict()}

@tasks_bp.put("/<task_id>")
def update_task(task_id):
    task = validate_model(Task, task_id)
    request_body = request.get_json()

    task.title = request_body["title"]
    task.description = request_body["description"]
    db.session.commit()

    response = {"task":task.to_dict()}
    return response

@tasks_bp.patch("/<task_id>/mark_complete")
def update_task_complete(task_id):
    task = validate_model(Task, task_id)

    task.completed_at = date.today()
    db.session.add(task)
    db.session.commit()

    response = {"task":task.to_dict()}
    return response

@tasks_bp.patch("/<task_id>/mark_incomplete")
def update_task_incomplete(task_id):
    task = validate_model(Task, task_id)

    task.completed_at = None
    db.session.add(task)
    db.session.commit()

    if create_slack_msg(task): 
        response = {"task":task.to_dict()}
        return response



@tasks_bp.delete("/<task_id>")
def delete_task(task_id):
    task = validate_model(Task, task_id)
    
    db.session.delete(task)
    db.session.commit()

    response = {"details": f'Task {task_id} \"{task.title}\" successfully deleted'}
    return response

def create_slack_msg(task):
    SECRET_KEY_SLACK = os.environ.get("SECRET_KEY_SLACK")

    header = {"Authorization": f"Bearer {SECRET_KEY_SLACK}"}
    params = {
        "channel": "D07GDA3R94P",
        "text": f"Someone just completed the task: {task.title}!"
    }

    return requests.post("https://slack.com/api/chat.postMessage", headers=header, params=params)