import bcrypt
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .data import USERS, ORDERS, ACCESS_RULES, BLACKLISTED_TOKENS
from .auth import create_token
from .permissions import check_permission

#auth

@api_view(["POST"])
def register(request):
    data = request.data

    required = ["first_name", "last_name", "email", "password", "password_confirm"]

    for f in required:
        if f not in data:
            return Response({"error": f"{f} is required"}, status=400)

    email = data["email"].strip().lower()

    if "@" not in email:
        return Response({"error": "Invalid email"}, status=400)

    if data["password"] != data["password_confirm"]:
        return Response({"error": "Passwords do not match"}, status=400)

    if any(u["email"] == email for u in USERS):
        return Response({"error": "Email exists"}, status=400)

    USERS.append({
        "id": len(USERS) + 1,
        "first_name": data["first_name"].strip(),
        "last_name": data["last_name"].strip(),
        "email": email,
        "password": bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt()),
        "role": "user",
        "is_active": True
    })

    return Response({"message": "User created"})


@api_view(["POST"])
def login(request):
    data = request.data

    if "email" not in data or "password" not in data:
        return Response({"error": "email and password required"}, status=400)

    email = data["email"].strip().lower()

    user = next((u for u in USERS if u["email"] == email), None)

    if not user or not user["is_active"]:
        return Response({"error": "Invalid credentials"}, status=400)

    if not bcrypt.checkpw(data["password"].encode(), user["password"]):
        return Response({"error": "Invalid credentials"}, status=400)

    return Response({"token": create_token(user)})


@api_view(["POST"])
def logout(request):
    auth = request.headers.get("Authorization")

    if not auth:
        return Response({"error": "Unauthorized"}, status=401)

    token = auth.split(" ")[1]
    BLACKLISTED_TOKENS.add(token)

    return Response({"message": "Logged out"})


@api_view(["GET"])
def me(request):
    if not request.auth_user:
        return Response({"error": "Unauthorized"}, status=401)

    return Response(request.auth_user)


#users

@api_view(["GET", "POST"])
def users_list(request):

    user = request.auth_user
    if not user:
        return Response({"error": "Unauthorized"}, status=401)

    # GET
    if request.method == "GET":
        if user["role"] == "admin":
            return Response(USERS)

        return Response([user])

    # POST (create user by admin)
    if not check_permission(user, "users", "create"):
        return Response({"error": "Forbidden"}, status=403)

    data = request.data

    required = ["first_name", "last_name", "email", "password"]

    for f in required:
        if f not in data:
            return Response({"error": f"{f} required"}, status=400)

    if any(u["email"] == data["email"] for u in USERS):
        return Response({"error": "Email exists"}, status=400)

    USERS.append({
        "id": len(USERS) + 1,
        "first_name": data["first_name"],
        "last_name": data["last_name"],
        "email": data["email"],
        "password": bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt()),
        "role": data.get("role", "user"),
        "is_active": True
    })

    return Response({"message": "User created"})


@api_view(["GET", "PATCH", "DELETE"])
def user_detail(request, user_id):

    user = request.auth_user
    if not user:
        return Response({"error": "Unauthorized"}, status=401)

    target = next((u for u in USERS if u["id"] == user_id), None)

    if not target:
        return Response({"error": "Not found"}, status=404)

    if not check_permission(user, "users", request.method.lower(), target["id"]):
        return Response({"error": "Forbidden"}, status=403)

    if request.method == "GET":
        return Response(target)

    if request.method == "PATCH":
        for f in ["first_name", "last_name", "email"]:
            if f in request.data:
                target[f] = request.data[f]

        return Response({"message": "Updated"})

    if request.method == "DELETE":
        target["is_active"] = False
        return Response({"message": "User deactivated"})


@api_view(["POST"])
def change_password(request, user_id):

    user = request.auth_user
    if not user:
        return Response({"error": "Unauthorized"}, status=401)

    target = next((u for u in USERS if u["id"] == user_id), None)

    if not target:
        return Response({"error": "Not found"}, status=404)

    if user["role"] != "admin" and user["id"] != user_id:
        return Response({"error": "Forbidden"}, status=403)

    data = request.data

    if user["role"] == "admin":
        required = ["new_password", "new_password_confirm"]
    else:
        required = ["old_password", "new_password", "new_password_confirm"]

    for f in required:
        if f not in data:
            return Response({"error": f"{f} is required"}, status=400)

    if data["new_password"] != data["new_password_confirm"]:
        return Response({"error": "Passwords do not match"}, status=400)

    if user["role"] != "admin":
        if not bcrypt.checkpw(data["old_password"].encode(), target["password"]):
            return Response({"error": "Wrong old password"}, status=400)

    target["password"] = bcrypt.hashpw(
        data["new_password"].encode(),
        bcrypt.gensalt()
    )

    return Response({"message": "Password updated"})


#orders

@api_view(["GET", "POST"])
def orders_list(request):

    user = request.auth_user
    if not user:
        return Response({"error": "Unauthorized"}, status=401)

    if request.method == "GET":
        if user["role"] == "admin":
            return Response(ORDERS)

        return Response([o for o in ORDERS if o["owner_id"] == user["id"]])

    if request.method == "POST":

        if not check_permission(user, "orders", "create"):
            return Response({"error": "Forbidden"}, status=403)

        data = request.data

        if not data.get("title"):
            return Response({"error": "title required"}, status=400)

        if user["role"] == "admin":
            owner_id = data.get("owner_id", user["id"])

            if not any(u["id"] == owner_id for u in USERS):
                return Response({"error": "Owner not found"}, status=400)
        else:
            owner_id = user["id"]

        order = {
            "id": len(ORDERS) + 1,
            "owner_id": owner_id,
            "title": data["title"]
        }

        ORDERS.append(order)

        return Response(order)


@api_view(["GET", "PATCH", "DELETE"])
def order_detail(request, order_id):

    user = request.auth_user
    if not user:
        return Response({"error": "Unauthorized"}, status=401)

    order = next((o for o in ORDERS if o["id"] == order_id), None)

    if not order:
        return Response({"error": "Not found"}, status=404)

    if not check_permission(user, "orders", request.method.lower(), order["owner_id"]):
        return Response({"error": "Forbidden"}, status=403)

    if request.method == "GET":
        return Response(order)

    if request.method == "PATCH":
        if "title" in request.data:
            order["title"] = request.data["title"]
        return Response(order)

    if request.method == "DELETE":
        ORDERS.remove(order)
        return Response({"message": "deleted"})


#rules

@api_view(["GET", "POST"])
def rules_list(request):

    user = request.auth_user
    if not user or user["role"] != "admin":
        return Response({"error": "Forbidden"}, status=403)

    if request.method == "GET":
        return Response(ACCESS_RULES)

    data = request.data

    ACCESS_RULES.append({
        "id": len(ACCESS_RULES) + 1,
        "role": data["role"],
        "element": data["element"],
        "action": data["action"],
        "value": data.get("value", False),
        "scope": data.get("scope", "all")
    })

    return Response({"message": "created"})


@api_view(["GET", "PATCH", "DELETE"])
def rule_detail(request, rule_id):

    user = request.auth_user
    if not user or user["role"] != "admin":
        return Response({"error": "Forbidden"}, status=403)

    rule = next((r for r in ACCESS_RULES if r["id"] == rule_id), None)

    if not rule:
        return Response({"error": "Not found"}, status=404)

    if request.method == "GET":
        return Response(rule)

    if request.method == "PATCH":
        for k in ["role", "element", "action", "value", "scope"]:
            if k in request.data:
                rule[k] = request.data[k]

        return Response(rule)

    if request.method == "DELETE":
        ACCESS_RULES.remove(rule)
        return Response({"message": "deleted"})
