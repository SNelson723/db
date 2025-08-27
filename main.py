from fastapi import FastAPI, Depends
import psycopg2
from routers.login import login
from routers.todos import todos
from routers.form import form
from db.db import get_db_connection
from utils import get_current_user
from schemas.schemas import TokenData
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/questions")
# defines the endpoint function => db parameter tells FastAPI to run the connection function and pass its result (a db connection) as the db argument
def get_questions(db=Depends(get_db_connection), current_user: TokenData = Depends(get_current_user)):
    # create a cursor object to execute SQL queries => used to execute sql queries and fetch results from the database
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
      # Execute a query to fetch all questions
      cursor.execute("SELECT * FROM questions")
      
      # Get column names from the result set
      column_names = [desc[0] for desc in cursor.description]
      
      # Fetch all rows returned from the executed query
      rows = cursor.fetchall()
      
      # Close the cursor after fetching the data to free up resources
      cursor.close()
      
      # Convert each row to a dictionary using column names
      # This builds a list of dictionaries for each row
      # zip(column_names, row) pairs each column name with its corresponding value in the row
      # dict(zip(...)) turns those pairs into a dictionary
      # This results in a list of dictionaries, where each dictionary represents a question with its attributes
      questions = [dict(zip(column_names, row)) for row in rows]
      
      # Return the questions in a structured format
      return {
          "success": True,
          "questions": questions,
          "error": 0
      }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error": 1
        }

app.include_router(login, prefix="/auth", tags=["auth"])
app.include_router(todos, prefix="/todos", tags=["todos"])
app.include_router(form, prefix="/form", tags=["form"])

# the command for running uvicorn on port 5000
# This allows React Native to also hit these endpoints
# uvicorn main:app --host 0.0.0.0 --reload --port 5000