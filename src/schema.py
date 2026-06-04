from typing import TypedDict, Optional, List, Dict

class PlannerState(TypedDict):
    user_query: str
    fitness_goals: Optional[str]
    body_composition: Optional[Dict]
    week_planning: Optional[List[str]]
    calorie_target: Optional[int]
    preferences: Optional[Dict]          # For Step 5
    found_locations: Optional[List[str]] # For Step 6
    selected_option: Optional[str]       # For Step 7
    final_workout_plan: Optional[str]    # For Step 8 & 9
    current_step: int
    is_step_valid: bool                  # Controls loops (Stap 3 & 5)