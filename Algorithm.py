import requests #requires pip install requests in terminal
import math
from itertools import combinations

# Vertice Class
class Vertex:
    def __init__(self, geolocation, gas, groceries, coffee, atm):
        self.geolocation = geolocation
        self.isGasStation = gas
        self.isGroceryStore = groceries
        self.isCoffeeShop = coffee
        self.isAtm = atm
        #self.edges = []


# Network Classs
class Network:
    def __init__(self, sourceLocation, destinationLocation, gas, groceries, coffee, atm):
        self.sourceLocation = sourceLocation  # string containg lat,lon
        self.destinationLocation = destinationLocation  # string containing lat,lon
        self.gasStation = gas  # bool, do we need to go to a gas station on the way?
        self.groceryStore = groceries  # bool, do we need to get groceries on the way?
        self.coffeeShop = coffee  # bool, do we need to get coffee on the way?
        self.atm = atm  # bool, do we need to go to an atm on the way?
        self.roundTrip = False
        self.vertices = []  # stores pointers to all vertices in our graph
        self.allPossiblePaths = [] #list of all the possible paths
        self.sourceVertex = Vertex(sourceLocation, False, False, False, False)
        self.maxPathSize = 1 #1 instead of 0 to account for the source vertex
        
        self.apiKey = "AIzaSyA6PBPaKmp9NxAjSy745SIH-Tp4wo1Oc68"  # Google Maps API Key from Samis account
        self.radius = 24140  # Radius in meters = 15 Miles

        if sourceLocation == destinationLocation:
            self.roundTrip = True
        else:
            # Source Address != destination Address
            self.destinationVertex = Vertex(destinationLocation, False, False, False, False)

        if (self.roundTrip == True):
            if gas == True:
                self.maxPathSize += 1
                self.initiateGasStations(sourceLocation)  # creates vertices for all gas stations
            if groceries == True:
                self.maxPathSize += 1
                self.initiateGroceryStores(sourceLocation)
            if coffee == True:
                self.maxPathSize += 1
                self.initiateCoffeeShops(sourceLocation)
            if atm == True:
                self.maxPathSize += 1
                self.initiateATMs(sourceLocation)
                
        if(self.roundTrip == False): #We are not doing a round trip
            latandlon = sourceLocation
            parts = latandlon.split(',')
            lat = float(parts[0])
            lon = float(parts[1])
            latandlon1 = destinationLocation
            parts1 = latandlon1.split(',')
            lat1 = float(parts1[0])
            lon1 = float(parts1[1])
            hyp = math.sqrt((self.latDifference)**2 + (self.lonDifference)**2)
            if ((70 * hyp) > 18):
                self.radius = 4828
                if gas == True:
                    self.maxPathSize += 1
                    self.initiateGasStations(destinationLocation)  # creates vertices for all gas stations
                if groceries == True:
                    self.maxPathSize += 1
                    self.initiateGroceryStores(destinationLocation)
                if coffee == True:
                    self.maxPathSize += 1
                    self.initiateCoffeeShops(destinationLocation)
                if atm == True:
                    self.maxPathSize += 1
                    self.initiateATMs(destinationLocation)
                    
        #Now that vertices are initialized, we create all the possible paths        
        self.constructAllPossiblePaths()
        
        #Finding shortest path via the lat lon coordinates
        self.currShortestPath = [] #will contain the shortest path once done
        self.currShortestPathsValue = float('inf');
        for path in self.allPossiblePaths:
            self.differences = []
            self.sumPath = 0;
            for vertex in path:
                self.latandlon = vertex.geolocation
                self.parts = self.latandlon.split(',')
                self.lat = float(self.parts[0])
                self.lon = float(self.parts[1])
                self.pairedUp = []
                self.pairedUp.append(self.lat)
                self.pairedUp.append(self.lon)
                self.differences.append(self.pairedUp)
            self.lastLon = 0
            self.lastLat = 0
            for element in self.differences:
                if (self.lastLon != 0 and self.lastLat !=0):
                    self.latDifference = abs(element[0] - self.lastLat)
                    self.lonDifference = abs(element[1] - self.lastLon)
                    self.lastLat = element[0]
                    self.lastLon = element[1]
                    self.hyp = math.sqrt((self.latDifference)**2 + (self.lonDifference)**2)
                    self.sumPath+=self.hyp
            if (self.sumPath < self.currShortestPathsValue):
                self.currShortestPath = path
                self.currShortestPathsValue = self.sumPath

    def getShortestPathArray(self):
        returnedList = []
        for element in self.currShortestPath:
            latandlon = element.geolocation
            parts = latandlon.split(',')
            part1 = str(parts[0])
            part2 = str(parts[1])
            result = part1 + "," + part2
            returnedList.append(result)
        return returnedList
            
    def addVertex(self, VertexInput):
        self.vertices.append(VertexInput)

    def initiateGasStations(self, location):
        api_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location}&radius={self.radius}&types=gas_station&key={self.apiKey}"
        response = requests.get(api_url)  # gets the response code to check

        if (response.status_code == 200):  # if the code returned == 200, it is a successful request
            data = response.json()  # data = content to JSON format
            gas_stations = data.get("results", [])  # gas stations = the "results" from the JSON file, else is empty list

            for (station) in gas_stations:  # iterates over each gas station object in the JSON file
                # Extracts information from each category
                station_location = station.get("geometry", {}).get("location", {})
                latitude = station_location.get("lat", "N/A")
                longitude = station_location.get("lng", "N/A")
                newGasStationVertice = Vertex(f"{latitude},{longitude}", True, False, False, False)
                self.addVertex(newGasStationVertice)
        else:
            print(f"Error: {response.status_code}")  # print the error status code
            print(response.text)  # print the corresponding text from the response

    def initiateGroceryStores(self, location):
        api_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location}&radius={self.radius}&types=grocery_or_supermarket&key={self.apiKey}"
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            grocery_stores = data.get("results", [])

            for store in grocery_stores:
                store_location = store.get("geometry", {}).get("location", {})
                latitude = store_location.get("lat", "N/A")
                longitude = store_location.get("lng", "N/A")
                newGroceryStoreVertex = Vertex(f"{latitude},{longitude}", False, True, False, False)
                self.addVertex(newGroceryStoreVertex)
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            
    def initiateCoffeeShops(self, location):
        api_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location}&radius={self.radius}&types=cafe&key={self.apiKey}"
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            coffee_shops = data.get("results", [])

            for shop in coffee_shops:
                shop_location = shop.get("geometry", {}).get("location", {})
                latitude = shop_location.get("lat", "N/A")
                longitude = shop_location.get("lng", "N/A")
                newCoffeeShopVertex = Vertex(f"{latitude},{longitude}", False, False, True, False)
                self.addVertex(newCoffeeShopVertex)
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            
    def initiateATMs(self, location):
        api_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location}&radius={self.radius}&types=atm&key={self.apiKey}"
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            atms = data.get("results", [])

            for atm in atms:
                atm_location = atm.get("geometry", {}).get("location", {})
                latitude = atm_location.get("lat", "N/A")
                longitude = atm_location.get("lng", "N/A")
                newATMVertex = Vertex(f"{latitude},{longitude}", False, False, False, True)
                self.addVertex(newATMVertex)

        else:
            print(f"Error: {response.status_code}")
            print(response.text)

    def constructAllPossiblePaths(self):
        n = len(self.vertices) #stores the count of vertices in our vertice list
        indices = list(range(n)) #creates a list called indices with values from 0 to n
        allCombinations = [] #stores all the combinations of indices
        
        for r in range(1, min(self.maxPathSize, len(indices) + 1)):
            uniqueCombinations = set(combinations(indices, r))
            for uniqueCombination in uniqueCombinations:
                currCombination = list(uniqueCombination)
                allCombinations.append(currCombination) #adds the current combination to the all combinations
        
        for path in allCombinations: #for each indice path...
            newPath = [] #stores the newPath
            newPath.append(self.sourceVertex) #Adds the source vertice to the beginning
            for element in path: #for each index in the path
                newPath.append(self.vertices[element])
            if (self.roundTrip == True):
                newPath.append(self.sourceVertex)
            else:
                newPath.append(self.destinationVertex)
            self.allPossiblePaths.append(newPath)
            
        #if its only gas and groceries, then its either gas gas, gas groceries, or groceries groceries
        pathsToBeRemoved = []
        for path in self.allPossiblePaths:
            gasExists = groceriesExists = coffeeExists = atmExists = False
            for vertex in path:
                if (vertex.isGasStation == True):
                    if (gasExists == True):
                        pathsToBeRemoved.append(path)
                    else:
                        gasExists = True
                if (vertex.isGroceryStore == True):
                    if (groceriesExists == True):
                        pathsToBeRemoved.append(path)
                    else:
                        groceriesExists = True
                if (vertex.isCoffeeShop == True):
                    if (coffeeExists == True):
                        pathsToBeRemoved.append(path)
                    else:
                        coffeeExists = True
                if (vertex.isAtm == True):
                    if (atmExists == True):
                        pathsToBeRemoved.append(path)
                    else:
                        atmExists = True
        for path in pathsToBeRemoved:
            for check in self.allPossiblePaths:
                if (path == check):
                    self.allPossiblePaths.remove(check)