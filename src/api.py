import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

from src.tools import calculate_fitness_calories
from src.nodes import ask_llm
from services.google_places import search_sport_locations, choose_best_locations


api = FastAPI()

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

api.mount("/ui", StaticFiles(directory="ui"), name="ui")

@api.get("/")
def root():
    return FileResponse("ui/index.html")


class StepRequest(BaseModel):
    step: str
    payload: Dict[str, Any]


@api.post("/api/step")
def handle_step(req: StepRequest):
    step = req.step
    p = req.payload

    if step == "refine_goal":
        goal = p.get("goal", "")
        refined = ask_llm(f"""The user entered this fitness goal: "{goal}"
        Rewrite it as a clean, short fitness goal in English (max 5 words).
        Only return the goal, nothing else.""")
        return {"refined_goal": refined.strip()}

    elif step == "validate_body":
        weight = p.get("weight")
        height = p.get("height")
        check = ask_llm(f"""A user entered weight: {weight}kg and height: {height}cm.
        Are these realistic human values? Reply with only YES or NO.""")
        return {"valid": "NO" not in check.upper()}

    elif step == "suggest_schedule":
        goal = p.get("goal", "")
        suggestion = ask_llm(f"""Suggest a 3-day gym weekly schedule for someone whose goal is: {goal}.
        Format it as exactly 3 lines like: "Monday: Push", "Wednesday: Pull", "Friday: Legs".
        Only return the 3 lines, nothing else.""")
        lines = [l.strip() for l in suggestion.strip().split("\n") if l.strip()]
        return {"schedule": lines}

    elif step == "calculate_calories":
        weight = p.get("weight")
        height = p.get("height")
        goal = p.get("goal", "")
        target_weight = p.get("target_weight")
        target_date = p.get("target_date")
        calories = calculate_fitness_calories(weight, height, goal, target_weight, target_date)
        return {"calories": calories}

    elif step == "search_gyms":
        prefs = p.get("preferences", {})
        location_type = prefs.get("location_type", "gym")

        if location_type == "home":
            return {"gyms": ["Home Workout"]}

        user_location = prefs.get("user_location", "Den Haag")
        workout_style = prefs.get("workout_style", "fitness")

        try:
            real_gyms = search_sport_locations(
                location=user_location,
                sport_preference=workout_style,
                max_results=5
            )

            best_gyms = choose_best_locations(real_gyms)

            gym_names = [
                gym["name"]
                for gym in best_gyms
                if gym.get("name")
            ]

            return {"gyms": gym_names if gym_names else ["No gyms found"]}

        except Exception as e:
            return {
                "gyms": ["Fallback Gym Network", "Local Community Center Gym"],
                "error": str(e)
            }

    elif step == "select_gym":
        goal = p.get("goal", "")
        prefs = p.get("preferences", {})
        gyms = p.get("gyms", [])

        if gyms == ["Home Workout"]:
            return {"selected": "Home Workout", "reason": "You chose to work out at home."}

        result = ask_llm(f"""The user's goal is: {goal}.
        Their preferences:
        - Workout style: {prefs.get('workout_style', 'unknown')}
        - Budget: {prefs.get('budget', 'unknown')}
        - Preferred time: {prefs.get('preferred_time', 'unknown')}
        - Intensity: {prefs.get('intensity', 'unknown')}
        Available gyms: {gyms}.
        Pick the single best gym and explain in one sentence why.
        Format exactly as: "GYM_NAME: reason" """)

        parts = result.split(":", 1)
        return {"selected": parts[0].strip(), "reason": parts[1].strip() if len(parts) > 1 else ""}

    elif step == "generate_plan":
        goal = p.get("goal", "")
        weight = p.get("weight")
        height = p.get("height")
        calories = p.get("calories")
        schedule = p.get("schedule", [])
        selected_gym = p.get("selected_gym", "")
        prefs = p.get("preferences", {})

        prompt = f"""Create a detailed workout and nutrition plan with the following details:

USER PROFILE:
- Goal: {goal}
- Weight: {weight}kg
- Height: {height}cm
- Daily calorie target: {calories} kcal

PREFERENCES:
- Location: {prefs.get('location_type', 'gym')}
- Workout style: {prefs.get('workout_style', 'free weights')}
- Preferred training time: {prefs.get('preferred_time', 'flexible')}
- Intensity level: {prefs.get('intensity', 'intermediate')}
- Weekly schedule: {schedule}
- Facility: {selected_gym}

Please include:
1. A day-by-day workout plan with specific exercises, sets, reps and rest times
2. Warm-up and cool-down routines
3. A daily nutrition breakdown (protein, carbs, fats)
4. Meal timing recommendations around workouts
5. Recovery tips tailored to the intensity level"""

        plan = ask_llm(prompt)

        summary = ask_llm(f"""Write a short motivating summary (2-3 sentences) for this fitness plan:
        Goal: {goal}, Calories: {calories} kcal/day, Gym: {selected_gym}, Intensity: {prefs.get('intensity')}""")

        return {"plan": plan, "summary": summary}

    return {"error": f"Unknown step: {step}"}