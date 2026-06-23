import jwt
import datetime

SECRET = "secret-key"
ALGO = "HS256"

def create_token(user):
    payload = {
        "user_id": user["id"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }
    return jwt.encode(payload, SECRET, algorithm=ALGO)


def decode_token(token):
    try:
        return jwt.decode(token, SECRET, algorithms=[ALGO])
    except:
        return None
