from fastapi import APIRouter, Depends
from db.db import get_db_connection
import psycopg2.extras

form = APIRouter()

@form.get('/all')
def get_all(db=Depends(get_db_connection)):
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute("SELECT * FROM form")
        forms = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        
        data = [dict(zip(column_names, row)) for row in forms]
        return {"success": True, "error": 0, "forms": data}
    except Exception as e:
        return {"success": False, "error": 1, "message": str(e)}
    finally:
        cursor.close()

@form.post('/submit_form')
def submit_form(name: str, email: str, db=Depends(get_db_connection)):
    print("Submitting form with name:", name, "and email:", email)
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cursor.execute("INSERT INTO form (name, email) VALUES (%s, %s)", (name, email))
        db.commit()
        return {"success": True, "error": 0, "message": "Form submitted successfully"}
    except Exception as e:
        return {"success": False, "error": 1, "message": str(e)}
    finally:
        cursor.close()