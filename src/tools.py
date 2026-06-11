import requests

def fetch_nearby_gyms_free() -> list:
    """
    Step 6 Tool: Uses the open-source OpenStreetMap Overpass API 
    to fetch real fitness facilities without using an account or API key.
    """
    print("🛰️ Connecting to OpenStreetMap Overpass API...")
    
    # Coordinates for Amsterdam area (Latitude, Longitude)
    lat, lon = 52.3676, 4.9041
    radius_meters = 2000 # 2km radius
    
    # Overpass QL query: Look for nodes/ways tagged as leisure=fitness_centre
    overpass_url = "https://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json][timeout:25];
    (
      node["leisure"="fitness_centre"](around:{radius_meters},{lat},{lon});
      way["leisure"="fitness_centre"](around:{radius_meters},{lat},{lon});
    );
    out tags;
    """
    
    try:
        response = requests.post(overpass_url, data={"data": overpass_query}, timeout=10)
        data = response.json()
        
        # Parse the elements and extract gym names
        gyms = []
        for element in data.get("elements", []):
            tags = element.get("tags", {})
            name = tags.get("name", "Unnamed Fitness Facility")
            gyms.append(name)
            
        # Return unique list up to top 3 gyms to keep it tidy
        return list(set(gyms))[:3]
        
    except Exception as e:
        print(f"❌ API Error: Could not reach OpenStreetMap ({e})")
        return ["Fallback Gym Network", "Local Community Center Gym"]

def calculate_fitness_calories(weight: float, height: float, fitness_goals: str, 
                                target_weight: float = None, target_date: str = None) -> int:
    # 1. Base BMR (assuming age 25)
    base_bmr = (10 * weight) + (6.25 * height) - (5 * 25) + 5
    
    # 2. TDEE with moderate activity
    tdee = int(base_bmr * 1.375)

    # 3. Calculate required adjustment if target weight and date are given
    if target_weight and target_date:
        weight_diff = target_weight - weight  # negative = need to lose, positive = need to gain

        # Parse timeframe into weeks
        date_lower = target_date.lower()
        if "week" in date_lower:
            weeks = float(''.join(filter(str.isdigit, date_lower)) or 12)
        elif "month" in date_lower:
            months = float(''.join(filter(str.isdigit, date_lower)) or 3)
            weeks = months * 4.33
        elif "year" in date_lower:
            years = float(''.join(filter(str.isdigit, date_lower)) or 1)
            weeks = years * 52
        else:
            weeks = 12  # default 3 months

        # 1kg of bodyweight ≈ 7700 kcal
        total_kcal_needed = weight_diff * 7700
        daily_adjustment = int(total_kcal_needed / (weeks * 7))

        # Cap adjustment at ±1000 kcal for safety
        daily_adjustment = max(-1000, min(1000, daily_adjustment))

        return tdee + daily_adjustment

    # 4. Fallback: simple goal-based adjustment (no target given)
    if "muscle" in fitness_goals.lower() or "aankomen" in fitness_goals.lower():
        return tdee + 300
    elif "lose" in fitness_goals.lower() or "afvallen" in fitness_goals.lower():
        return tdee - 400

    return tdee