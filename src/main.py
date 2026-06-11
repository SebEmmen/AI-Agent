from langgraph.graph import StateGraph, START, END
from src.schema import PlannerState
from src.nodes import (
    step_1_fitness_goals, 
    step_2_body_composition, 
    step_3_week_planning,
    herstel_step_3,
    step_4_calculate_calories,
    step_5_preferences,
    herstel_step_5,
    step_6_search_locations,
    step_7_choose_best_option,
    step_8_create_workout_plan,
    step_9_final_presentation
)

# 1. Initialize Graph
workflow = StateGraph(PlannerState)

# 2. Register ALL Nodes
workflow.add_node("stap_1", step_1_fitness_goals)
workflow.add_node("stap_2", step_2_body_composition)
workflow.add_node("stap_3", step_3_week_planning)
workflow.add_node("herstel_3", herstel_step_3)
workflow.add_node("stap_4", step_4_calculate_calories)
workflow.add_node("stap_5", step_5_preferences)
workflow.add_node("herstel_5", herstel_step_5)
workflow.add_node("stap_6", step_6_search_locations)
workflow.add_node("stap_7", step_7_choose_best_option)
workflow.add_node("stap_8", step_8_create_workout_plan)
workflow.add_node("stap_9", step_9_final_presentation)

# 3. Add Linear Edges
workflow.add_edge(START, "stap_1")
workflow.add_edge("stap_1", "stap_2")
workflow.add_edge("stap_2", "stap_3")
workflow.add_edge("herstel_3", "stap_3")
workflow.add_edge("stap_4", "stap_5")
workflow.add_edge("herstel_5", "stap_5")
workflow.add_edge("stap_6", "stap_7")
workflow.add_edge("stap_7", "stap_8")
workflow.add_edge("stap_8", "stap_9")
workflow.add_edge("stap_9", END)

# 4. Routing Routers
def router_step_3(state: PlannerState):
    return "continue" if state["is_step_valid"] else "backtrack"

def router_step_5(state: PlannerState):
    return "continue" if state["is_step_valid"] else "backtrack"

# 5. Connect Conditional Edges
workflow.add_conditional_edges(
    "stap_3", router_step_3, 
    {"continue": "stap_4", "backtrack": "herstel_3"}
)
workflow.add_conditional_edges(
    "stap_5", router_step_5, 
    {"continue": "stap_6", "backtrack": "herstel_5"}
)

# 6. Compile
app = workflow.compile()

if __name__ == "__main__":
    # Initialize an empty starting state dictionary
    initial_state = {
        "user_query": "",
        "fitness_goals": None,
        "target_weight": None,     # ← new
        "target_date": None,       # ← new
        "body_composition": None,
        "week_planning": None,
        "calorie_target": None,
        "preferences": None,
        "found_locations": None,
        "selected_option": None,
        "final_workout_plan": None,
        "current_step": 1,
        "is_step_valid": True
    }
    
    # Fire up the compiler app!
    app.invoke(initial_state)