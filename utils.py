from datetime import datetime, timedelta
from jose import jwt

secret_key = '3ec626139eed86a4e0e94feb44ec6bf9035eb385b2d041822a08f0ac59ba5ecf'
algorithm = 'HS256'
access_token_expire_minutes = 120  # 2 hours

def generate_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(datetime.now().utc) + timedelta(minutes=access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt