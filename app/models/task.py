from sqlalchemy.orm import Mapped, mapped_column
from ..db import db
from typing import Optional
from datetime import datetime

class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    description: Mapped[str] 
    completed_at: Mapped[Optional[datetime]] 


    def to_dict(self):
        is_complete_flag = False 
        if self.completed_at: 
            is_complete_flag = True

        return dict(
            id=self.id,
            title=self.title, 
            description=self.description,
            is_complete = is_complete_flag
        )
    
    @classmethod
    def from_dict(cls, task_data): 
        return cls( 
            title=task_data["title"], 
            description=task_data["description"]
        )