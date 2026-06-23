from .auth import decode_token
from .data import BLACKLISTED_TOKENS
from .data import USERS

class AuthMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        request.auth_user = None

        auth = request.headers.get("Authorization")

        if auth and auth.startswith("Bearer "):
            token = auth.split(" ")[1]

            if token not in BLACKLISTED_TOKENS:
                payload = decode_token(token)

                if payload:
                    user = next((u for u in USERS if u["id"] == payload["user_id"]), None)
                    if user and user["is_active"]:
                        request.auth_user = user

        return self.get_response(request)
