import json
from datetime import date
from pathlib import Path

USAGE_FILE = Path("api_usage.json")
DAILY_LIMIT = 150


def can_make_google_places_call() -> bool:
    """
    Controleert of er vandaag nog een Google Places API-call gemaakt mag worden.
    """

    today = str(date.today())

    if not USAGE_FILE.exists():
        return True

    with open(USAGE_FILE, "r", encoding="utf-8") as file:
        usage = json.load(file)

    return usage.get(today, 0) < DAILY_LIMIT


def register_google_places_call() -> None:
    """
    Registreert één succesvolle Google Places API-call voor vandaag.
    """

    today = str(date.today())

    if USAGE_FILE.exists():
        with open(USAGE_FILE, "r", encoding="utf-8") as file:
            usage = json.load(file)
    else:
        usage = {}

    usage[today] = usage.get(today, 0) + 1

    with open(USAGE_FILE, "w", encoding="utf-8") as file:
        json.dump(usage, file, indent=4)