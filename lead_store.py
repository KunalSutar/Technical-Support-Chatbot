import json
import os

FILE = "sales_leads.json"

# ensure file exists
if not os.path.exists(FILE):
    with open(FILE, "w") as f:
        json.dump({}, f, indent=2)


def load_leads():
    with open(FILE, "r") as f:
        return json.load(f)


def save_leads(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)


def update_lead(session_id, company_name=None, team_size=None, use_case=None):
    data = load_leads()

    if session_id not in data:
        data[session_id] = {
            "company_name": None,
            "team_size": None,
            "use_case": None,
        }

    if company_name:
        data[session_id]["company_name"] = company_name

    if team_size:
        data[session_id]["team_size"] = team_size

    if use_case:
        data[session_id]["use_case"] = use_case

    save_leads(data)
