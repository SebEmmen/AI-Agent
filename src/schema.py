from typing import TypedDict, Optional, List, Dict

class PlannerState(TypedDict):
    user_query: str
    fitness_goals: Optional[str]
    target_weight: Optional[float]    # ← new
    target_date: Optional[str]        # ← new
    body_composition: Optional[Dict]
    week_planning: Optional[List[str]]
    calorie_target: Optional[int]
    preferences: Optional[Dict]
    found_locations: Optional[List[str]]
    selected_option: Optional[str]
    final_workout_plan: Optional[str]
    current_step: int
    is_step_valid: bool