from sqlalchemy.orm import Session
from database import SessionLocal, engine
from utils.models import Users

# Create the database tables
Users.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create a new todo item
def create_todo_item(id: str, username: str):
    db = next(get_db())
    new_todo = Users(id=id, username=username)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

# Read all todo items
def get_todo_items():
    db = next(get_db())
    return db.query(Users).all()

# Update a todo item
def update_todo_item(id: int, username: str):
    db = next(get_db())
    todo_item = db.query(Users).filter(Users.id == id).first()
    if todo_item:
        todo_item.username = username
        db.commit()
        db.refresh(todo_item)
    return todo_item

# Delete a todo item
def delete_todo_item(id: int):
    db = next(get_db())
    todo_item = db.query(Users).filter(Users.id == id).first()
    if todo_item:
        db.delete(todo_item)
        db.commit()
    return todo_item

# Example usage
if __name__ == "__main__":
    # Create a new todo item
    # create_todo_item("Buy groceries", "Milk, Bread, Eggs")

    # Get all todo items
    todos = get_todo_items()
    print(todos)

    # Update a todo item
    # update_todo_item(1, "Buy groceries and fruits", "Milk, Bread, Eggs, Apples")

    # Delete a todo item
    # delete_todo_item(2)