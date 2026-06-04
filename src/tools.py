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

def calculate_fitness_calories(weight: float, height: float, fitness_goals: str) -> int:
    """
    Step 4 Tool: Calculates daily calorie targets using a simplified 
    Harris-Benedict formula (assuming a baseline moderate activity multiplier).
    """
    # 1. Calculate base Basal Metabolic Rate (BMR) for a generic profile
    # Formula: 10 * weight (kg) + 6.25 * height (cm) - (5 * age) + 5
    # Let's assume a default age of 25 for school project simplicity
    base_bmr = (10 * weight) + (6.25 * height) - (5 * 25) + 5
    
    # 2. Factor in moderate daily activity multiplier (TDEE = BMR * 1.375)
    tdee = int(base_bmr * 1.375)
    
    # 3. Adjust calories based on the goal stored in the state
    if "muscle" in fitness_goals.lower() or "aankomen" in fitness_goals.lower():
        # Caloric surplus to build muscle
        return tdee + 300
    elif "lose" in fitness_goals.lower() or "afvallen" in fitness_goals.lower():
        # Caloric deficit to lose weight
        return tdee - 400
    
    return tdee