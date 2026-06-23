import bcrypt

def hash_password(p):
    return bcrypt.hashpw(p.encode(), bcrypt.gensalt())

USERS = [
    {
        "id": 1,
        "email": "admin@test.com",
        "first_name":"Admin",
        "last_name":"Testov",
        "password": hash_password("1234"),
        "role": "admin",
        "is_active": True
    },
    {
        "id": 2,
        "email": "user@test.com",
        "first_name":"Users",
        "last_name":"Testov",
        "password": hash_password("1234"),
        "role": "user",
        "is_active": True
    }
]

ORDERS = [
    {"id": 1, "owner_id": 2, "title": "Order1"},
    {"id": 2, "owner_id": 2, "title": "Order2"},
]

ACCESS_RULES = [
    {
        "id": 1,
        "role": "admin",
        "element": "*",
        "action": "*",
        "value": True,
        "scope": "all"
    },
    {
        "id": 2,
        "role": "user",
        "element": "orders",
        "action": "create",
        "value": True,
        "scope": "own"
    }
]

BLACKLISTED_TOKENS = set()
