from flask import Blueprint, abort, make_response, request, Response
from app.models.task import Task
from app.db import db

task_bp = Blueprint("task_bp", __name__, url_prefix="/tasks")

@task_bp.post("")
def create_task(): 
    request_body = request.get_json()
    title = request_body["title"]
    description = request_body["description"]
    # is_complete = request_body["is_complete"]

    new_task = Task(title=title, description=description)
    # new_task = Task(title=title, description=description, is_complete=is_complete)

    db.session.add(new_task)
    db.session.commit()

    response = new_task.to_dict()
    return response, 201


@task_bp.get("")
def get_all_tasks(): 
    query = db.select(Task)
    title_param = request.args.get("title")
    if title_param:
        query = query.where(Task.title.ilike(f"%{title_param}%"))
    
    query=query.order_by(Task.id)
    tasks = db.session.scalars(query)

    tasks_response =[task.to_dict() for task in tasks]


    return tasks_response