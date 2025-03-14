# models.py
import json
from config import INGREDIENTS_FILE

class Ingredient:
    def __init__(self, id_entity, name, cost, uom, conversionUnits=""):
        self.id_entity = id_entity
        self.name = name
        self.cost = cost
        self.uom = uom
        self.conversionUnits = conversionUnits

def load_ingredients():
    """Load ingredients from the JSON file."""
    with open(INGREDIENTS_FILE, 'r') as f:
        data = json.load(f)
    # You can choose to convert these to Ingredient instances if needed:
    # return [Ingredient(**item) for item in data]
    return data
