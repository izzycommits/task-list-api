from flask import Blueprint, abort, make_response, request, Response
from app.models.task import Task
from app.db import db

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@tasks_bp.post("")
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


@tasks_bp.get("/<planet_id>")
def get_single_planet(planet_id):
    planet = validate_planet(planet_id)

    return planet.to_dict()

@tasks_bp.put("/<planet_id>")
def update_planet(planet_id):
    planet = validate_planet(planet_id)
    request_body = request.get_json()

    planet.name = request_body["name"]
    planet.description = request_body["description"]
    db.session.commit()

    return Response(status = 204, mimetype = "application/json")

@tasks_bp.delete("/<planet_id>")
def delete_planet(planet_id):
    planet = validate_planet(planet_id)
    
    db.session.delete(planet)
    db.session.commit()

    return Response(status = 204, mimetype = "application/json")

def validate_planet(task_id):
    try:
        task_id = int(task_id)
    except ValueError: 
        abort(make_response({"message":f"Task id {task_id} is invalid"}, 400))

    query = db.select(Task).where(Task.id == task_id)
    task = db.session.scalar(query)

    if not task:
        abort(make_response({"message":f"Task id {task_id} is not found"}, 404))

    return task