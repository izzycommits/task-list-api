from flask import Blueprint, abort, make_response, request, Response
from app.models.task import Task
from app.db import db

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@tasks_bp.post("")
def create_task(): 
    request_body = request.get_json()
    title = request_body["title"]
    description = request_body["description"]

    new_task = Task(title=title, description=description)

    db.session.add(new_task)
    db.session.commit()

    response = new_task.to_dict()
    return response, 201


@tasks_bp.get("")
def get_all_tasks(): 
    query = db.select(Task)
    title_param = request.args.get("title")
    if title_param:
        query = query.where(Task.title.ilike(f"%{title_param}%"))
    
    query=query.order_by(Task.id)
    tasks = db.session.scalars(query)

    tasks_response =[task.to_dict() for task in tasks]

    return tasks_response


@tasks_bp.get("/<task_id>")
def get_single_task(task_id):
    task = validate_task(task_id)

    return {"task":task.to_dict()}

@tasks_bp.put("/<task_id>")
def update_task(task_id):
    task = validate_task(task_id)
    request_body = request.get_json()

    task.name = request_body["name"]
    task.description = request_body["description"]
    db.session.commit()

    return Response(status = 204, mimetype = "application/json")

@tasks_bp.delete("/<task_id>")
def delete_task(task_id):
    task = validate_task(task_id)
    
    db.session.delete(task)
    db.session.commit()

    return Response(status = 204, mimetype = "application/json")

def validate_task(task_id):
    try:
        task_id = int(task_id)
    except ValueError: 
        abort(make_response({"message":f"Task id {task_id} is invalid"}, 400))

    query = db.select(Task).where(Task.id == task_id)
    task = db.session.scalar(query)

    if not task:
        abort(make_response({"message":f"Task id {task_id} is not found"}, 404))

    return task