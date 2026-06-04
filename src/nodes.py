from src.schema import PlannerState
from src.tools import calculate_fitness_calories, fetch_nearby_gyms_free

def step_1_fitness_goals(state: PlannerState):
    print("\n=========================================")
    print("🤖 AGENT: Welkom bij je Fitness Planner!")
    print("=========================================")
    
    # Take real input from the keyboard
    user_goal = input("👉 Wat is je belangrijkste fitnessdoel? (bijv. Build muscle / Lose weight): ")
    
    return {"fitness_goals": user_goal, "user_query": user_goal, "current_step": 1}

def step_2_body_composition(state: PlannerState):
    print("\n🤖 AGENT: Laten we je lichaamssamenstelling bekijken.")
    
    try:
        weight = float(input("👉 Wat is je gewicht in kg? (alleen getallen): "))
        height = float(input("👉 Wat is je lengte in cm? (alleen getallen): "))
        return {"body_composition": {"weight": weight, "height": height}, "current_step": 2}
    except ValueError:
        print("❌ Systeemfout: Voer aanzienlijke getallen in. We proberen stap 2 opnieuw.")
        # This will just re-run step 2 safely
        return step_2_body_composition(state)

def step_3_week_planning(state: PlannerState):
    print(f"\n🤖 AGENT: Op basis van je doel '{state['fitness_goals']}' stel ik voor: Maandag (Push) en Woensdag (Pull).")
    choice = input("👉 Komt deze weekplanning je goed uit? (ja / nee): ").strip().lower()
    
    if choice == "ja":
        return {"week_planning": ["Monday: Push", "Wednesday: Pull"], "is_step_valid": True, "current_step": 3}
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
    user_pref = input("👉 Wat is je budget of locatievoorkeur? (Typ 'euro' om de validatie te passeren): ")
    
    if "euro" not in user_pref.lower():
        return {"is_step_valid": False, "user_query": user_pref, "current_step": 5}
    
    return {"preferences": {"input": user_pref}, "is_step_valid": True, "current_step": 5}

def herstel_step_5(state: PlannerState):
    print("\n🔄 [HERSTELACTIE STAP 5] Budget details ontbreken in je antwoord!")
    retry_pref = input("👉 Geef aub je budget op in euro's (bijv. 50 euro): ")
    return {"user_query": "Budget is " + retry_pref, "is_step_valid": True}

def step_6_search_locations(state: PlannerState):
    print("\n--- [NODE] Step 6: Fetching Sports Locations (Live OpenStreetMap API) ---")
    
    # Execute the live API query
    real_gyms = fetch_nearby_gyms_free()
    print(f"📍 API Result: Found gyms nearby: {real_gyms}")
    
    return {"found_locations": real_gyms, "current_step": 6}

def step_7_choose_best_option(state: PlannerState):
    print("--- [NODE] Step 7: Selecting Best Match ---")
    
    # Pick the first gym from the real API response gathered in Step 6
    if state["found_locations"]:
        best_match = state["found_locations"][0]
    else:
        best_match = "Home Workout Routine"
        
    print(f"🎯 Choice: Automatically matching user with: {best_match}")
    return {"selected_option": best_match, "current_step": 7}

def step_8_create_workout_plan(state: PlannerState):
    print("\n🤖 AGENT: Je definitieve fitness- en voedingsplan genereren...")
    return {"final_workout_plan": "Volledig Split Schema + Voedingsrichtlijnen", "current_step": 8}

def step_9_final_presentation(state: PlannerState):
    print("--- [NODE] Step 9: Presenting Plan to User ---")
    print(f"\n🎉 HERE IS YOUR DYNAMIC PLAN:")
    print(f"Target Calories : {state['calorie_target']} kcal per day matched to your goal: '{state['fitness_goals']}'")
    print(f"Assigned Facility: {state['selected_option']} (Fetched live via API!)")
    return {"current_step": 9}