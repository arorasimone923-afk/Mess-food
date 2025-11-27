from flask import Flask, render_template, request, jsonify
import pandas as pd
import joblib
import os

app = Flask(__name__)

# Load the files YOU created
df = pd.read_csv('mess_food_database.csv')

# Load the AI model if available
try:
    model = joblib.load('nutrition_model.pkl')
    model_loaded = True
    print("✅ AI Model loaded successfully!")
except:
    model_loaded = False
    print("ℹ️ Using rule-based calculator")

class NutritionCalculator:
    def __init__(self, nutrition_db):
        self.db = nutrition_db
    
    def find_food(self, food_name):
        """Smart food matching"""
        matches = self.db[self.db['food_item'].str.contains(food_name, case=False, na=False)]
        return matches
    
    def calculate_meal(self, food_items):
        """Calculate nutrition for multiple foods"""
        total = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'fiber': 0}
        
        for food, quantity in food_items.items():
            match = self.find_food(food)
            if not match.empty:
                food_data = match.iloc[0]
                ratio = quantity / 100
                total['calories'] += food_data['calories'] * ratio
                total['protein'] += food_data['protein_g'] * ratio
                total['carbs'] += food_data['carbs_g'] * ratio
                total['fat'] += food_data['fat_g'] * ratio
                total['fiber'] += food_data['fiber_g'] * ratio
                print(f"✅ {food}: {quantity}g")
            else:
                print(f"❌ {food}: Not found")
        
        return total

calculator = NutritionCalculator(df)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        food_items = data.get('food_items', {})
        
        result = calculator.calculate_meal(food_items)
        
        return jsonify({
            'success': True,
            'nutrition': result,
            'message': 'Nutrition calculated successfully!'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/foods')
def get_foods():
    """Get list of available foods for autocomplete"""
    foods = df['food_item'].tolist()
    return jsonify(foods)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)