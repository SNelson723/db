from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from schemas.schemas import LoginRequest, User
from db.db import get_db_connection
from passlib.context import CryptContext
import psycopg2.extras
from utils import generate_token

login = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@login.post('/login')
def login_user(request: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db_connection)):
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        
        # Get the user by username
        cursor.execute("SELECT * FROM users WHERE username = %s", (request.username,))
        user = cursor.fetchone()
        
        # If no user is found, return an error response
        if user is None:
            return JSONResponse(status_code=401, content={"success": False, "error": 2, "authenticated": False})
          
        # The password is accessible from the user dictionary established by psycopg2.extras.DictCursor
        # This allows us to access the password field directly
        hashed_password = user['password']
        
        # If the password does not match, return an error response
        # pwd_context.verify() checks the provided password against the hashed password
        if not pwd_context.verify(request.password, hashed_password):
            return JSONResponse(status_code=401, content={"success": False, "error": 1, "msg": "Invalid username or password"})
          
        # Generate a token for the user => the generate_token function creates a JWT token with the user's username
        access_token = generate_token(data={"username": user['username']})
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        return JSONResponse(status_code=401, content={"success": False, "error": 1, "msg": str(e)})
    finally:
        # Ensure the cursor is closed even if an error occurs
        if cursor:
            cursor.close()

  
@login.post('/create')
def create_user(request: User, db=Depends(get_db_connection)):
  # Create the cursor object to execute SQL queries
  cursor = db.cursor()
  try:
    
    # Check if the username already exists
    cursor.execute("SELECT * FROM users WHERE username = %s", (request.username,))
    existing_user = cursor.fetchone()
    
    # If the username already exists, return an error response
    if existing_user:
        return JSONResponse(status_code=400, content={"success": False, "error": 1, "msg": "Username already exists"})
    
    # If the email already exists, return an error response
    cursor.execute("SELECT * FROM users WHERE email = %s", (request.email,))
    existing_email = cursor.fetchone()
    if existing_email:
        return JSONResponse(status_code=400, content={"success": False, "error": 1, "msg": "Email already exists"})
    
    # Use the password hashing context to hash the password
    hashed_password = pwd_context.hash(request.password)
    
    # Execute the query with parameters to prevent SQL injection and commit the transaction
    cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", (request.username, hashed_password, request.email))
    db.commit()

    # Return a success response
    return {"success": True, "error": 0}
  
  # Handle any exceptions that occur during the process
  except Exception as e:
    return JSONResponse(status_code=400, content={"success": False, "error": 1, "msg": str(e)})
  finally:
    # Ensure the cursor is closed even if an error occurs
    if cursor:
        cursor.close()