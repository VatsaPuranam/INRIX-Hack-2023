let map; // Reference to the map object
let directionsService; // Service to compute directions
let directionsRenderer; 
let autocompleteStart, autocompleteEnd; // Autocomplete objects
let isRoundTrip = false;
function initMapAndAutocomplete() {
    // Initialize the map
    const map = new google.maps.Map(document.getElementById('map'), {
      zoom: 12,
      center: { lat: 37.7749, lng: -122.4194 }, // San Francisco coordinates
    });
     // Initialize the directions service and renderer
    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer();
    directionsRenderer.setMap(map);
    
    // Initialize the autocomplete functionality
    autocompleteStart = new google.maps.places.Autocomplete(
      document.getElementById('starting-location'),
      { types: ['geocode'] }
    );
    autocompleteEnd = new google.maps.places.Autocomplete(
      document.getElementById('ending-location'),
      { types: ['geocode'] }
    );
  
    // Bias the Autocomplete objects to the user's geographical location, if possible
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((position) => {
        const geolocation = {
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        };
        const circle = new google.maps.Circle({
          center: geolocation,
          radius: position.coords.accuracy,
        });
        autocompleteStart.setBounds(circle.getBounds());
        autocompleteEnd.setBounds(circle.getBounds());
      });
    }
  
    // Event listeners for autocomplete objects to do something when a user selects a location
    autocompleteStart.addListener('place_changed', () => {
      const place = autocompleteStart.getPlace();
      if (place.geometry) {
        map.panTo(place.geometry.location);
      } else {
        console.log("No details available for input: '" + place.name + "'");
      }
    });
  
    autocompleteEnd.addListener('place_changed', () => {
      const place = autocompleteEnd.getPlace();
      if (place.geometry) {
        map.panTo(place.geometry.location);
      } else {
        console.log("No details available for input: '" + place.name + "'");
      }
    });
  }
  
  // Other event listeners and functions can remain the same
  // ...
  
  // Make sure the initMapAndAutocomplete function is available globally
window.initMapAndAutocomplete = initMapAndAutocomplete;
function displayRouteOnMap(routeCoordinates) {
    if (directionsRenderer) {
      directionsRenderer.setMap(null); // Clear previous routes
    }
    directionsRenderer.setMap(map);
  
    // If round trip, make sure the route ends at the starting point
    if (isRoundTrip) {
      routeCoordinates.push(routeCoordinates[0]);
    }
  
    // Create a DirectionsRequest from the returned path
    const origin = routeCoordinates[0]; // First coordinate is the origin
    const destination = routeCoordinates[routeCoordinates.length - 1]; // Last coordinate is the destination
    const waypoints = routeCoordinates.slice(1, -1).map(coord => ({ location: coord, stopover: true }));
  
    const request = {
      origin: origin,
      destination: destination,
      waypoints: waypoints,
      travelMode: google.maps.TravelMode.DRIVING,
      optimizeWaypoints: isRoundTrip // Optimize waypoints only if round trip is enabled
    };
  
    directionsService.route(request, (result, status) => {
      if (status === 'OK') {
        directionsRenderer.setDirections(result);
      } else {
        console.error('Directions request failed due to ' + status);
      }
    });
  }
  

document.addEventListener('DOMContentLoaded', () => {
  const startingLocationInput = document.getElementById('starting-location');
  const endingLocationInput = document.getElementById('ending-location');
  const roundTripButton = document.getElementById('round-trip-button');
  const optimizeButton = document.getElementById('optimizeButton');

  roundTripButton.addEventListener('click', () => {
      isRoundTrip = !isRoundTrip;
      if (isRoundTrip) {
          endingLocationInput.value = startingLocationInput.value;
          roundTripButton.textContent = 'Round Trip Enabled';
      } else {
          endingLocationInput.value = '';
          roundTripButton.textContent = 'Click for round trip';
      }
  });
  
    function optimizeErrands(startingLocation, endingLocation, errands, roundTrip) {
      // Placeholder for optimization logic
      // This would be where you implement your algorithm or API calls
      //call the google maps api on starting location, and ending location to pass strings as long lat;
      // console.log(`Optimizing errands from ${startingLocation} to ${endingLocation} with round trip: ${roundTrip}`);
      // console.log('Selected errands:', errands);
  
      // Return a mock optimized plan
      // return errands; // In real scenario, this would be the optimized order of errands
    }
  
    function displayOptimizedPlan(plan) {
      // Placeholder for displaying the plan to the user
      console.log('Optimized Plan:', plan);
      // Update the DOM with the optimized plan details
    }
      // Event listener for the optimize button
      // Inside the event listener for the optimize button
    optimizeButton.addEventListener('click', () => {
        const startPlace = autocompleteStart.getPlace();
        const endPlace = autocompleteEnd.getPlace();
        console.log(startPlace);
        console.log(endPlace);

        // Assuming you have a way to get the boolean values for each errand
        const gas = document.getElementById('gas-checkbox').checked;
        const groceries = document.getElementById('groceries-checkbox').checked;
        const coffee = document.getElementById('coffee-checkbox').checked;
        const atm = document.getElementById('atm-checkbox').checked;
        console.log(gas);
        console.log(groceries);
        console.log(coffee);
        console.log(atm);

        if (!startPlace.geometry || !endPlace.geometry) {
            console.log("Returned place contains no geometry");
            return;
        }

        const startCoords = `${startPlace.geometry.location.lat()},${startPlace.geometry.location.lng()}`;
        const endCoords = `${endPlace.geometry.location.lat()},${endPlace.geometry.location.lng()}`;
        console.log(startCoords);
        console.log(endCoords);

        // Now send this data to the Python server
        fetch('http://localhost:5000/optimize_errands', {
            method: 'POST',
            mode:'cors',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sourceLocation: startCoords,
                destinationLocation: endCoords,
                gas: gas,
                groceries: groceries,
                coffee: coffee,
                atm: atm
            })
        })
        .then(response => {
            if (!response.ok) {
              throw new Error('Network response was not ok: ' + response.statusText);
            }
            return response.json();
          })
          .then(data => {
            if (data.path) {
              // Transform the path into Google Maps LatLng objects
              const routeCoordinates = data.path.map(coord => new google.maps.LatLng(coord.lat, coord.lng));
              displayRouteOnMap(routeCoordinates);
            } else {
              throw new Error('Path data is missing from the response');
            }
          })
          .catch(error => {
            console.error('Fetch error:', error);
          });
    });
});

window.initMapAndAutocomplete = initMapAndAutocomplete;

  