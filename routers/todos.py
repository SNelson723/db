from fastapi import APIRouter, Depends
from db.db import get_db_connection
import psycopg2.extras

from schemas.schemas import TokenData
from utils import get_current_user

todos = APIRouter()

# Testing my function
@todos.get('/test')
def test_function(is_complete: bool, user_id: int, db=Depends(get_db_connection), current_user: TokenData = Depends(get_current_user)):
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute('SELECT * FROM usp_get_uncompleted_tasks(%s, %s)', (is_complete, user_id))
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        todos = [dict(zip(column_names, row)) for row in rows]
        return {"success": True, "error": 0, "todos": todos}
    except Exception as e:
        return {"success": False, "error": 1, "message": str(e)}
    finally:
        cursor.close()

# GET
@todos.get('/get_todos')
def get_todos(id: int, db=Depends(get_db_connection), current_user: TokenData = Depends(get_current_user)):
  cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
  try:
      cursor.execute("SELECT * FROM todos WHERE user_id = %s", (id,))
      rows = cursor.fetchall()
      column_names = [desc[0] for desc in cursor.description]
      
      todos = [dict(zip(column_names, row)) for row in rows]
      
      if todos:
          return {"success": True, "error": 0, "todos": todos}
      return {"success": False, "error": 2, "message": "Todos not found"}
  except Exception as e:
      return {"success": False, "error": 1, "message": str(e)}
  finally:
      cursor.close()
      
@todos.get('/get_category')
def get_category(user_id: int, category: str, db=Depends(get_db_connection), current_user: TokenData = Depends(get_current_user)):
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute("SELECT * FROM todos WHERE user_id = %s AND LOWER(category) = LOWER(%s)", (user_id, category))
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        
        # Convert rows to a list of dictionaries
        todos = [dict(zip(column_names, row)) for row in rows]

        if todos:
            return {"success": True, "error": 0, "todos": todos}
        return {"success": False, "error": 2, "message": "Todos not found"}
    except Exception as e:
        return {"success": False, "error": 1, "message": str(e)}
    finally:
        cursor.close()

# POST
@todos.post('/add_todo')
def add_todo(task: str, is_complete: bool, user_id: int, category: str, db=Depends(get_db_connection), current_user: TokenData = Depends(get_current_user)):
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute("INSERT INTO todos (todo, complete, user_id, category) VALUES (%s, %s, %s, %s) RETURNING id", (task, is_complete, user_id, category))
        todo_id = cursor.fetchone()[0]
        
        db.commit()
        return {"success": True, "error": 0, "message": "Todo added successfully", "todo_id": todo_id}
    except Exception as e:
        db.rollback()
        return {"success": False, "error": 1, "message": str(e)}
    finally:
        cursor.close()

# PUT
@todos.put('/update_task')
def update_task(
    todo_id: int,
    task: str,
    user_id: int,
    db=Depends(get_db_connection),
    current_user: TokenData = Depends(get_current_user)
):
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute(
            "UPDATE todos SET todo = %s WHERE id = %s AND user_id = %s RETURNING *",
            (task, todo_id, user_id)
        )
        updated_todo = cursor.fetchone()
        db.commit()
        
        if updated_todo:
            # Convert to dict if needed
            return {
                "success": True,
                "error": 0,
                "message": "Task updated successfully",
                "todo": dict(updated_todo)
            }
        else:
            return {"success": False, "error": 2, "message": "Todo not found"}
    except Exception as e:
        db.rollback()
        return {"success": False, "error": 1, "message": str(e)}
    finally:
        cursor.close()

@todos.put('/update_status')
def update_status(todo_id: int, is_complete: bool, user_id: int, db=Depends(get_db_connection), current_user: TokenData = Depends(get_current_user)):
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute(
            "UPDATE todos SET complete = %s WHERE id = %s AND user_id = %s RETURNING *",
            (is_complete, todo_id, user_id)
        )
        updated_todo = cursor.fetchone()
        db.commit()

        if updated_todo:
            return {
                "success": True,
                "error": 0,
                "message": "Status updated successfully",
                "todo": dict(updated_todo)
            }
        else:
            return {"success": False, "error": 2, "message": "Todo not found"}
    except Exception as e:
        db.rollback()
        return {"success": False, "error": 1, "message": str(e)}
    finally:
        cursor.close()

# DELETE
@todos.delete('/delete_todo')
def delete_todo(todo_id: int, user_id: int, db=Depends(get_db_connection), current_user: TokenData = Depends(get_current_user)):
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute("DELETE FROM todos WHERE id = %s AND user_id = %s RETURNING *", (todo_id, user_id))
        deleted_todo = cursor.fetchone()
        db.commit()

        if deleted_todo:
            return {"success": True, "error": 0, "message": "Todo deleted successfully", "todo": dict(deleted_todo)}
        else:
            return {"success": False, "error": 2, "message": "Todo not found"}
    except Exception as e:
        db.rollback()
        return {"success": False, "error": 1, "message": str(e)}
    finally:
        cursor.close()