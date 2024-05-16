# Python script (app.py)

from flask import Flask, redirect, render_template, request, url_for
from pymongo import MongoClient
from bson import ObjectId  # Add this import statement

app = Flask(__name__, template_folder='templates')
client = MongoClient('mongodb://localhost:27017/')
db = client['hospitality_database']
collection = db['hotels']

@app.route('/')
def index():
    hotels = collection.find()
    return render_template('index.html', hotels=hotels)

@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.form.get('query')
    if query:
        # Search hotels by location or name
        hotels = collection.find({
            '$or': [
                {'location': {'$regex': query, '$options': 'i'}},  # Case-insensitive regex search
                {'name': {'$regex': query, '$options': 'i'}}
            ]
        })
    else:
        hotels = collection.find()  # If no query provided, return all hotels
    return render_template('index.html', hotels=hotels)


from flask import jsonify

@app.route('/hotels/nearby')
def find_hotels_nearby():
    longitude = float(request.args.get('longitude'))
    latitude = float(request.args.get('latitude'))

    nearby_hotels = collection.find({
        'location': {
            '$nearSphere': {
                '$geometry': {
                    'type': 'Point',
                    'coordinates': [longitude, latitude]
                },
                '$maxDistance': 10000  # Adjust the maximum distance as needed (in meters)
            }
        }
    })



@app.route('/hotel_detail/<hotel_id>')
def hotel_detail(hotel_id):
    # Here you would fetch the hotel information from MongoDB based on the hotel_id
    # Replace the placeholder code below with actual MongoDB queries
    # Example: hotel = get_hotel_by_id(hotel_id)
    hotel = collection.find_one({"_id": ObjectId(hotel_id)})
    return render_template('hotel_detail.html', hotel=hotel)

@app.route('/submit_review/<hotel_id>', methods=['POST'])
def submit_review(hotel_id):
    # Extract review data from the form submission
    author = request.form['author']
    rating = int(request.form['rating'])
    comment = request.form['comment']
    
    # Create a new review object
    review = {
        'author': author,
        'rating': rating,
        'comment': comment
    }
    
    # Update the hotel document with the new review
    collection.update_one({'_id': ObjectId(hotel_id)}, {'$push': {'reviews': review}})
    
    # Redirect the user back to the hotel detail page
    return redirect(url_for('hotel_detail', hotel_id=hotel_id))

if __name__ == '__main__':
    app.run(debug=True)
