# nodes.py

import os
from dotenv import load_dotenv
from groq import Groq
from src.schema import PlannerState
from src.tools import calculate_fitness_calories, fetch_nearby_gyms_free
from services.google_places import search_sport_locations, choose_best_locations

load_dotenv()  # ← add this line before the client is created

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def ask_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def step_1_fitness_goals(state: PlannerState):
    print("\n=========================================")
    print("🤖 AGENT: Welkom bij je Fitness Planner!")
    print("=========================================")
    
    user_goal = input("👉 Wat is je belangrijkste fitnessdoel? (bijv. Build muscle / Lose weight): ")
    
    # LLM cleans and standardises the goal
    refined = ask_llm(f"""The user entered this fitness goal: "{user_goal}"
    Rewrite it as a clean, short fitness goal in English (max 5 words).
    Only return the goal, nothing else.""")
    
    print(f"🤖 Understood goal: {refined}")
    return {"fitness_goals": refined, "user_query": user_goal, "current_step": 1}

def step_2_body_composition(state: PlannerState):
    print("\n🤖 AGENT: Laten we je lichaamssamenstelling bekijken.")
    
    try:
        weight = float(input("👉 Wat is je gewicht in kg? (alleen getallen): "))
        height = float(input("👉 Wat is je lengte in cm? (alleen getallen): "))
        
        # LLM checks if the numbers are realistic
        check = ask_llm(f"""A user entered weight: {weight}kg and height: {height}cm.
        Are these realistic human values? Reply with only YES or NO.""")
        
        if "NO" in check.upper():
            print("❌ These values don't seem realistic, please try again.")
            return step_2_body_composition(state)
        
        return {"body_composition": {"weight": weight, "height": height}, "current_step": 2}
    except ValueError:
        print("❌ Voer aanzienlijke getallen in. We proberen stap 2 opnieuw.")
        return step_2_body_composition(state)

def step_3_week_planning(state: PlannerState):
    # LLM suggests a schedule based on the goal
    suggestion = ask_llm(f"""Suggest a 3-day gym weekly schedule for someone whose goal is: {state['fitness_goals']}.
    Format it as exactly 3 lines like: "Monday: Push", "Wednesday: Pull", "Friday: Legs".
    Only return the 3 lines, nothing else.""")
    
    print(f"\n🤖 AGENT: Op basis van je doel stel ik voor:\n{suggestion}")
    choice = input("👉 Komt deze weekplanning je goed uit? (ja / nee): ").strip().lower()
    
    if choice == "ja":
        schedule = [line.strip() for line in suggestion.strip().split("\n") if line.strip()]
        return {"week_planning": schedule, "is_step_valid": True, "current_step": 3}
    else:
        return {"is_step_valid": False, "current_step": 3}

def herstel_step_3(state: PlannerState):
    print("\n🔄 [HERSTELACTIE STAP 3] De planning paste niet.")
    input("👉 Welke dagen of aanpassingen zou je in plaats daarvan willen? (Druk op Enter om door te gaan): ")
    # Forcing it to be true on retry for testing convenience
    return {"is_step_valid": True}

def step_4_calculate_calories(state: PlannerState):
    print("\n🤖 AGENT: Berekenen van je energiebehoefte met de wiskundige tool...")
    weight = state["body_composition"]["weight"]
    height = state["body_composition"]["height"]
    goals = state["fitness_goals"]
    
    calculated_calories = calculate_fitness_calories(weight, height, goals)
    return {"calorie_target": calculated_calories, "current_step": 4}

def step_5_preferences(state: PlannerState):
    print("\n🤖 AGENT: Voorkeuren, Locatie & Budget controleren.")
    
    # Question 1: Home or gym
    print("\n📍 Where do you want to work out?")
    print("  1. At a gym")
    print("  2. At home")
    location_type = input("👉 Enter 1 or 2: ").strip()
    location_type = "gym" if location_type == "1" else "home"

    # Question 2: If gym, classes or weights
    workout_style = "home workout"
    if location_type == "gym":
        print("\n🏋️ What type of gym experience do you prefer?")
        print("  1. Free weights / machines only")
        print("  2. Group classes (yoga, spinning, HIIT, etc.)")
        print("  3. Both weights and classes")
        style_choice = input("👉 Enter 1, 2, or 3: ").strip()
        styles = {"1": "free weights and machines", "2": "group classes", "3": "both weights and classes"}
        workout_style = styles.get(style_choice, "free weights and machines")

    # Question 3: Preferred workout times
    print("\n⏰ When do you prefer to work out?")
    print("  1. Early morning (6-9am)")
    print("  2. Afternoon (12-3pm)")
    print("  3. Evening (5-8pm)")
    time_choice = input("👉 Enter 1, 2, or 3: ").strip()
    times = {"1": "early morning", "2": "afternoon", "3": "evening"}
    preferred_time = times.get(time_choice, "flexible")

    # Question 4: Location and budget (only if gym)
    user_location = "Den Haag"
    budget = "none"

    if location_type == "gym":
        user_location = input("\n📍 In welke stad of plaats wil je zoeken naar sportscholen? ").strip()

        if not user_location:
            user_location = "Den Haag"

        budget = input("\n💶 What is your monthly gym budget in euros? (e.g. 40 euro): ").strip()

    # Question 5: Workout intensity
    print("\n💪 What intensity level do you prefer?")
    print("  1. Beginner (lighter weights, more rest)")
    print("  2. Intermediate (moderate challenge)")
    print("  3. Advanced (high intensity, heavy weights)")
    intensity_choice = input("👉 Enter 1, 2, or 3: ").strip()
    intensities = {"1": "beginner", "2": "intermediate", "3": "advanced"}
    intensity = intensities.get(intensity_choice, "intermediate")

    preferences = {
        "location_type": location_type,
        "user_location": user_location,
        "workout_style": workout_style,
        "preferred_time": preferred_time,
        "budget": budget,
        "intensity": intensity,
        "input": f"{budget}, {location_type}, {user_location}, {workout_style}, {preferred_time}, {intensity}"
    }

    print(f"\n✅ Preferences saved: {location_type} | {workout_style} | {preferred_time} | {intensity}")
    return {"preferences": preferences, "is_step_valid": True, "current_step": 5}


def herstel_step_5(state: PlannerState):
    print("\n🔄 [HERSTELACTIE STAP 5] Budget details ontbreken in je antwoord!")
    retry_pref = input("👉 Geef aub je budget op in euro's (bijv. 50 euro): ")
    updated = state.get("preferences", {})
    updated["budget"] = retry_pref
    updated["input"] = retry_pref
    return {"preferences": updated, "user_query": "Budget is " + retry_pref, "is_step_valid": True}


def step_6_search_locations(state: PlannerState):
    print("\n--- [NODE] Step 6: Fetching Sports Locations with Google Places API ---")

    prefs = state.get("preferences", {})
    location_type = prefs.get("location_type", "gym")

    if location_type == "home":
        print("🏠 User prefers home workouts, skipping gym search.")
        return {"found_locations": ["Home Workout"], "current_step": 6}

    user_location = prefs.get("user_location", "Den Haag")
    workout_style = prefs.get("workout_style", "fitness")

    try:
        real_gyms = search_sport_locations(
            location=user_location,
            sport_preference=workout_style,
            max_results=5
        )

        best_gyms = choose_best_locations(real_gyms)

        print(f"📍 Found gyms with Google Places: {best_gyms}")

        gym_names = [
            gym["name"]
            for gym in best_gyms
            if gym.get("name")
        ]

        return {
            "found_locations": gym_names if gym_names else ["No gyms found"],
            "current_step": 6
        }

    except Exception as e:
        print(f"❌ Google Places API error: {e}")
        return {
            "found_locations": ["Fallback Gym Network", "Local Community Center Gym"],
            "current_step": 6
        }
    print("\n--- [NODE] Step 6: Fetching Sports Locations ---")

    prefs = state.get("preferences", {})
    location_type = prefs.get("location_type", "gym")

    # Skip API call entirely if user wants home workout
    if location_type == "home":
        print("🏠 User prefers home workouts, skipping gym search.")
        return {"found_locations": ["Home Workout"], "current_step": 6}

    real_gyms = fetch_nearby_gyms_free()
    print(f"📍 Found gyms: {real_gyms}")

    filtered = ask_llm(f"""The user has these preferences:
    - Budget: {prefs.get('budget', 'unknown')}
    - Workout style: {prefs.get('workout_style', 'unknown')}
    - Preferred time: {prefs.get('preferred_time', 'unknown')}
    
    These gyms were found nearby: {real_gyms}.
    Which gyms best fit the user's preferences? Return only the gym names as a comma-separated list.
    If none fit well, return the full list.""")

    filtered_list = [g.strip() for g in filtered.split(",")]
    print(f"🤖 LLM filtered to: {filtered_list}")
    return {"found_locations": filtered_list, "current_step": 6}


def step_7_choose_best_option(state: PlannerState):
    print("--- [NODE] Step 7: Selecting Best Match ---")

    prefs = state.get("preferences", {})

    if state["found_locations"] == ["Home Workout"]:
        return {"selected_option": "Home Workout", "current_step": 7}

    best = ask_llm(f"""The user's goal is: {state['fitness_goals']}.
    Their preferences:
    - Workout style: {prefs.get('workout_style', 'unknown')}
    - Budget: {prefs.get('budget', 'unknown')}
    - Preferred time: {prefs.get('preferred_time', 'unknown')}
    - Intensity: {prefs.get('intensity', 'unknown')}
    
    Available gyms: {state['found_locations']}.
    Pick the single best gym and explain in one sentence why.
    Format exactly as: "GYM_NAME: reason" """)

    gym_name = best.split(":")[0].strip()
    print(f"🎯 LLM chose: {best}")
    return {"selected_option": gym_name, "current_step": 7}


def step_8_create_workout_plan(state: PlannerState):
    print("\n🤖 AGENT: Je definitieve fitness- en voedingsplan genereren...")

    prefs = state.get("preferences", {})

    prompt = f"""Create a detailed workout and nutrition plan with the following details:

    USER PROFILE:
    - Goal: {state['fitness_goals']}
    - Weight: {state['body_composition']['weight']}kg
    - Height: {state['body_composition']['height']}cm
    - Daily calorie target: {state['calorie_target']} kcal

    PREFERENCES:
    - Location: {prefs.get('location_type', 'gym')}
    - Workout style: {prefs.get('workout_style', 'free weights')}
    - Preferred training time: {prefs.get('preferred_time', 'flexible')}
    - Intensity level: {prefs.get('intensity', 'intermediate')}
    - Weekly schedule: {state['week_planning']}
    - Facility: {state['selected_option']}

    Please include:
    1. A day-by-day workout plan with specific exercises, sets, reps and rest times
    2. Warm-up and cool-down routines
    3. A daily nutrition breakdown (protein, carbs, fats)
    4. Meal timing recommendations around workouts
    5. Recovery tips tailored to the intensity level"""

    plan = ask_llm(prompt)
    return {"final_workout_plan": plan, "current_step": 8}

def step_9_final_presentation(state: PlannerState):
    print("--- [NODE] Step 9: Presenting Plan ---")
    
    summary = ask_llm(f"""Write a short motivating summary (3-4 sentences) for this fitness plan:
    - Goal: {state['fitness_goals']}
    - Calories: {state['calorie_target']} kcal/day
    - Schedule: {state['week_planning']}
    - Gym: {state['selected_option']}
    - Full plan: {state['final_workout_plan']}""")
    
    print(f"\n🎉 YOUR PLAN:")
    print(f"Calories : {state['calorie_target']} kcal/day")
    print(f"Facility : {state['selected_option']}")
    print(f"\n{summary}")
    print(f"\n--- FULL PLAN ---\n{state['final_workout_plan']}")
    
    return {"current_step": 9}