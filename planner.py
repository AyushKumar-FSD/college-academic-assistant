import datetime as dt
import json

from prompts import PLAN, PLAN_EDIT


def create(ask_json, subjects, days, hours, total, context, start):
    plan = ask_json(PLAN, subjects=", ".join(subjects), days=days, hours=hours, total=total,
                    context=context or "none")["plan"]
    return [{**d, "date": (start + dt.timedelta(i)).strftime("%a %d %b")} for i, d in enumerate(plan)]


def modify(ask_json, plan, request):
    return ask_json(PLAN_EDIT, plan=json.dumps(plan), request=request)["plan"]
