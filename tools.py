import math

# We add type hints (: float, : str) so the AI doesn't crash
def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str):
    """
    Calculates Basal Metabolic Rate (BMR) using the Mifflin-St Jeor Equation.
    """
    if gender.lower() == "male":
        return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:
        return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161

def calculate_macros(weight_kg: float, goal: str):
    """
    Returns specific macronutrient targets. 
    Goal: 'Lose Fat', 'Build Muscle', 'Maintain'
    """
    # Ensure inputs are numbers (safety check)
    weight_kg = float(weight_kg)
    
    protein = int(weight_kg * 2.0)
    fats = int(weight_kg * 0.8)
    
    if goal == "Lose Fat":
        carbs = int(weight_kg * 2.0)
    elif goal == "Build Muscle":
        carbs = int(weight_kg * 4.0)
    else:
        carbs = int(weight_kg * 3.0)
        
    return {"protein": protein, "fats": fats, "carbs": carbs}