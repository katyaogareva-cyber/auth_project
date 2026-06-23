from .data import ACCESS_RULES

def check_permission(user, element, action, obj_owner_id=None):

    if user["role"] == "admin":
        return True

    rules = [
        r for r in ACCESS_RULES
        if r["role"] == user["role"]
        and r["element"] in (element, "*")
        and r["action"] in (action, "*")
    ]

    if not rules:
        return False

    for r in rules:

        if not r["value"]:
            continue

        scope = r.get("scope", "all")

        if scope == "all":
            return True

        if scope == "own":
            if obj_owner_id is not None and obj_owner_id == user["id"]:
                return True

    return False
