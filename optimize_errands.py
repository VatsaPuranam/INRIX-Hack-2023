import os
import requests
from flask import Flask, request, jsonify #jsonify is used to get the arguments from front end
from flask_cors import CORS

from Algorithm import Network

app = Flask(__name__)
CORS(app)

def get_api_token():
    app_id = "l0bav9j9dl"  # Ideally, this should be an environment variable
    hash_token = "bDBiYXY5ajlkbHxQSWNWdk1La3lzOFYxblI5Smo2d3o5ak5icDFJR2tFYjM1THh2WDRW"  # And this too
    url = f"https://api.iq.inrix.com/auth/v1/appToken?appId={app_id}&hashToken={hash_token}"

    try:
        # Query INRIX for token
        response = requests.get(url)
        response.raise_for_status()  # This will raise an exception for HTTP errors

        # Parse the JSON response
        json_response = response.json()
        token = json_response.get('result', {}).get('token')

        if token:
            return token  # Return just the token if you're going to use it in Python
        else:
            raise ValueError("Token not found in response")
    
    except requests.RequestException as e:
        # Handle any request-related errors here
        print(f"HTTP Request failed: {e}")
        return None
    except ValueError as e:
        # Handle missing token error here
        print(f"Token retrieval failed: {e}")
        return None

    
@app.route('/optimize_errands', methods=['GET']) #data retrieval from the server
def optimize_errands(): #this function will be called when the /optimize_errands endpoint is accessed
    pass
    if not request.is_json: #checks if we did get data
        return jsonify({"error": "No Json File was returned!"}), 400
    data = request.get_json()
    
    source_location = data['sourceLocation']
    destination_location = data['destinationLocation']
    gas = data['gas']
    groceries = data['groceries']
    coffee = data['coffee']
    atm = data['atm']
    optimize_errands_post(source_location,destination_location,gas,groceries,coffee,atm)
    
@app.route('/optimize_errands', methods=['POST']) #data retrieval from the server
def optimize_errands_post(source_location,destination_location,gas,groceries,coffee,atm): #this function will be called when the /optimize_errands endpoint is accessed
    # Call your Python function here with the coordinates and errands
    optimized_path = Network(source_location, destination_location, gas, groceries, coffee, atm)
    returnedListOfGeolocations = optimized_path.getShortestPathArray()
    
    #Calling the INRIX api here
    apiToken = get_api_token()
    
    # Build the URL based on the number of geolocations
    base_url = "https://api.iq.inrix.com/findRoute"
    waypoints = '&'.join([f"wp_{i+1}={loc}" for i, loc in enumerate(returnedListOfGeolocations)])
    api_url = f"{base_url}?{waypoints}&routeOutputFields=P&format=json&accessToken={apiToken}"
    
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        coordinates = data.get("coordinates", [])
        for pair in coordinates:
            location = pair.get("geometry", {}).get("location", {})
            latitude = location.get("lat", "N/A")
            longitude = location.get("lng", "N/A")
        
    return jsonify(coordinates)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)