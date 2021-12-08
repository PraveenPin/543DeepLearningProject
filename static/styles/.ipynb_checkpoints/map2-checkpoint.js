
let labelIndex = 0;
let map;
// Pickup marker is index 0 and drop off marker is index 1
let markers = [];
let turn = 0;
const newyork = { lat: 40.730610, lng: -73.935242 };
const NEW_YORK_BOUNDS = {
  north: 30.00,
  south: 50.00,
  west: -70.00,
  east: -80.00,
};
let ridePath;
const JFK = { lat: 40.641766, lng: -73.780968 };

function initFullscreenControl(map) {
  const elementToSendFullscreen = map.getDiv().firstChild;
  const fullscreenControl = document.querySelector(".fullscreen-control");

  map.controls[google.maps.ControlPosition.RIGHT_TOP].push(fullscreenControl);
  fullscreenControl.onclick = function () {
    if (isFullscreen(elementToSendFullscreen)) {
      exitFullscreen();
    } else {
      requestFullscreen(elementToSendFullscreen);
    }
  };

  document.onwebkitfullscreenchange =
    document.onmsfullscreenchange =
    document.onmozfullscreenchange =
    document.onfullscreenchange =
      function () {
        if (isFullscreen(elementToSendFullscreen)) {
          fullscreenControl.classList.add("is-fullscreen");
        } else {
          fullscreenControl.classList.remove("is-fullscreen");
        }
      };
}

function isFullscreen(element) {
  return (
    (document.fullscreenElement ||
      document.webkitFullscreenElement ||
      document.mozFullScreenElement ||
      document.msFullscreenElement) == element
  );
}

function requestFullscreen(element) {
  if (element.requestFullscreen) {
    element.requestFullscreen();
  } else if (element.webkitRequestFullScreen) {
    element.webkitRequestFullScreen();
  } else if (element.mozRequestFullScreen) {
    element.mozRequestFullScreen();
  } else if (element.msRequestFullScreen) {
    element.msRequestFullScreen();
  }
}

function exitFullscreen() {
  if (document.exitFullscreen) {
    document.exitFullscreen();
  } else if (document.webkitExitFullscreen) {
    document.webkitExitFullscreen();
  } else if (document.mozCancelFullScreen) {
    document.mozCancelFullScreen();
  } else if (document.msExitFullscreen) {
    document.msExitFullscreen();
  }
}

function initZoomControl(map) {
  console.log("Map",map);
  document.querySelector(".zoom-control-in").onclick = function () {
    map.setZoom(map.getZoom() + 1);
  };

  document.querySelector(".zoom-control-out").onclick = function () {
    map.setZoom(map.getZoom() - 1);
  };

  map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(
    document.querySelector(".zoom-control")
  );
}

function CenterControl(controlDiv, map) {
  // Set CSS for the control border.
  const controlUI = document.createElement("div");

  controlUI.style.backgroundColor = "#fff";
  controlUI.style.border = "2px solid #fff";
  controlUI.style.borderRadius = "3px";
  controlUI.style.boxShadow = "0 2px 6px rgba(0,0,0,.3)";
  controlUI.style.cursor = "pointer";
  controlUI.style.marginTop = "8px";
  controlUI.style.marginBottom = "22px";
  controlUI.style.textAlign = "center";
  controlUI.title = "Click to recenter the map";
  controlDiv.appendChild(controlUI);

  // Set CSS for the control interior.
  const controlText = document.createElement("div");

  controlText.style.color = "rgb(25,25,25)";
  controlText.style.fontFamily = "Roboto,Arial,sans-serif";
  controlText.style.fontSize = "16px";
  controlText.style.lineHeight = "38px";
  controlText.style.paddingLeft = "5px";
  controlText.style.paddingRight = "5px";
  controlText.innerHTML = "Center Map";
  controlUI.appendChild(controlText);
  // Setup the click event listeners: simply set the map to Chicago.
  controlUI.addEventListener("click", () => {
    map.setCenter(newyork);
  });
}


function initMap() {
  map = new google.maps.Map(document.getElementById("map"), {
    zoom: 12,
    center: newyork,
    disableDefaultUI: true,
    restriction: {
      latLngBounds: NEW_YORK_BOUNDS,
      strictBounds: false,
    }
  });
  initZoomControl(map);
  initFullscreenControl(map);

  // Create the DIV to hold the control and call the CenterControl()
  // constructor passing in this DIV.
  const centerControlDiv = document.createElement("div");

  CenterControl(centerControlDiv, map);
  map.controls[google.maps.ControlPosition.TOP_CENTER].push(centerControlDiv);

  if(!!map){
    // This event listener calls addMarker() when the map is clicked.
    google.maps.event.addListener(map, "click", (event) => {
      console.log("Lat long:",event.latLng.lat());
      addMarker(event.latLng, map);
    });
    // Add a marker at the center of the map.
    addMarker(newyork, map);
  }
}

function deleteMarkers() {
  setMapOnAll(null);
  markers = [];
}

// Sets the map on all markers in the array.
function setMapOnAll(map) {
  for (let i = 0; i < markers.length; i++) {
    markers[i].setMap(map);
  }
}

// Adds a marker to the map.
function addMarker(location, map) {
  // Add the marker at the clicked location, and add the next-available label
  // from the array of alphabetical characters.
  const pickupMarker = {
    path: "M10.453 14.016l6.563-6.609-1.406-1.406-5.156 5.203-2.063-2.109-1.406 1.406zM12 2.016q2.906 0 4.945 2.039t2.039 4.945q0 1.453-0.727 3.328t-1.758 3.516-2.039 3.070-1.711 2.273l-0.75 0.797q-0.281-0.328-0.75-0.867t-1.688-2.156-2.133-3.141-1.664-3.445-0.75-3.375q0-2.906 2.039-4.945t4.945-2.039z",
    fillColor: "blue",
    fillOpacity: 0.6,
    strokeWeight: 0,
    rotation: 0,
    scale: 2,
    anchor: new google.maps.Point(15, 30),
  };

  const DropMarker = {
    path: "M10.453 14.016l6.563-6.609-1.406-1.406-5.156 5.203-2.063-2.109-1.406 1.406zM12 2.016q2.906 0 4.945 2.039t2.039 4.945q0 1.453-0.727 3.328t-1.758 3.516-2.039 3.070-1.711 2.273l-0.75 0.797q-0.281-0.328-0.75-0.867t-1.688-2.156-2.133-3.141-1.664-3.445-0.75-3.375q0-2.906 2.039-4.945t4.945-2.039z",
    fillColor: "green",
    fillOpacity: 0.9,
    strokeWeight: 0,
    rotation: 0,
    scale: 2,
    anchor: new google.maps.Point(15, 30),
  };

  let numberOfMarkers = markers.length;
  const marker = new google.maps.Marker({
    position: location,
    icon: numberOfMarkers == 0 ? pickupMarker : numberOfMarkers == 1 ? DropMarker : turn == 0 ? pickupMarker : DropMarker,
    // label: numberOfMarkers == 0 ? 'P' : 'D',
    map: map,
  });

  console.log("Number of maerkers:",numberOfMarkers);
  // deleteMarkers();
  setMapOnAll(null);
  if(numberOfMarkers == 0){
    markers.push(marker);
  }
  else if(numberOfMarkers == 2){
    // markers[turn].setMap(map);
    markers[turn] = marker;
    turn = (turn+1)%2;
  }
  else{
    markers[1] = marker;
  }

  setMapOnAll(map);
  if(!!ridePath){
    ridePath.setMap(null);
  }

  if (markers.length == 2){
    const pathCoordinates = [{ lat: markers[0].position.lat(), lng: markers[0].position.lng() }, { lat: markers[1].position.lat(), lng: markers[1].position.lng() }];
    ridePath = new google.maps.Polyline({
      path: pathCoordinates,
      geodesic: true,
      strokeColor: "#FF0000",
      strokeOpacity: 1.0,
      strokeWeight: 5,
    });

    ridePath.setMap(map);
  }
}



function submit(){
  let xhr = new XMLHttpRequest();
  let url = "getFare";


  const form  = document.getElementById('submitFareForm');
  console.log("form svalue",form['passengers'].value);
  if(markers.length < 2){
    alert('Please select both pickup and drop off locations');
    return;
  }
  const pathCoordinates = [{ lat: markers[0].position.lat(), lng: markers[0].position.lng() }, { lat: markers[1].position.lat(), lng: markers[1].position.lng() }];

  const passengers = form['passengers'].value;
  const date = form['date'].value;
  const time = form['time'].value;

  const d = new Date(date);
  let splitData = date.split('-');
  const year = splitData[0];
  const month = splitData[1];
  const day = splitData[2];
  const weekday = d.getDate();

  let splitTime = time.split(':');
  const hour = splitTime[0];
  const minute = splitTime[1];

  const pickup_latitude = pathCoordinates[0].lat;
  const pickup_longitude = pathCoordinates[0].lng;
  const dropoff_latitude = pathCoordinates[1].lat;
  const dropoff_longitude = pathCoordinates[1].lng;

  console.log("pickup:",pickup_latitude,pickup_longitude);
  console.log("dropoff:",dropoff_latitude,dropoff_longitude);

  console.log("date and time:",year,month,day,hour,minute);

  // open a connection
  xhr.open("POST", url, true);

  const original_pickup_latitude = pickup_latitude;
  const original_pickup_longitude = pickup_longitude;
  const original_dropoff_latitude = dropoff_latitude;
  const original_dropoff_longitude = dropoff_longitude;

  // Set the request header i.e. which type of content you are sending
  xhr.setRequestHeader("Content-Type", "application/json");

  // Create a state change callback
  xhr.onreadystatechange = function () {
      if (xhr.readyState === 4 && xhr.status === 200) {

          // Print received data from server
          console.log("Respo:",JSON.parse(this.responseText));
          var res=JSON.parse(this.responseText);
          var table = document.getElementById('t1');
          table.innerHTML=''
          console.log("Table",table)
          var tr1 = document.createElement('tr');
    var td11 = document.createElement('td');
    var td12 = document.createElement('td');
      var td13= document.createElement('td');
        var td14 = document.createElement('td');
          var td15 = document.createElement('td');
     var text11 = document.createTextNode("Fare");
    var text12 = document.createTextNode("Distancd");
    var text13= document.createTextNode("Km");
    var text14 = document.createTextNode("pickup Location");
    var text15 = document.createTextNode("dropp");
      tr1.appendChild(td12);
     tr1.appendChild(td13);
      tr1.appendChild(td14);
       tr1.appendChild(td15);
    table.appendChild(tr1);
for (var i = 1; i < 7; i++){
    var tr = document.createElement('tr');

    var td1 = document.createElement('td');
    var td2 = document.createElement('td');
      var td3= document.createElement('td');
        var td4 = document.createElement('td');
          var td5 = document.createElement('td');


    var text1 = document.createTextNode(res[0].fare);
    var text2 = document.createTextNode(res[0].pickup_latitude);
    var text3= document.createTextNode(res[0].pickup_latitude);
    var text4 = document.createTextNode(res[0].pickup_latitude);
    var text5 = document.createTextNode(res[0].pickup_latitude);

    td1.appendChild(text1);
    td2.appendChild(text2);
    td3.appendChild(text3);
    td4.appendChild(text4);
    td5.appendChild(text5);


    td11.appendChild(text11);
    td12.appendChild(text12);
    td13.appendChild(text13);
    td14.appendChild(text14);
    td15.appendChild(text15);
    tr.appendChild(td1);
    tr.appendChild(td2);
     tr.appendChild(td3);
      tr.appendChild(td4);
       tr.appendChild(td5);
       tr1.appendChild(td11);

    table.appendChild(tr);
}

          console.log("wlwmw",res[0].pickup_latitude);
JSC.Chart('chartDiv', {
   type: 'vertical column',
   series: [
      {
         points: [
            {x:'aaple', y:40}

         ]
      }
   ]
});

          //near_by_rides = [[-74.004277, -74.001712, 40.74272, 40.751197, 5.0, 2014.0, 'month', 'day', 'time', 'distance_km' ,"distance_to_new_pickup"]];

//         distance_to_new,pickup_point, plat, plong, dlat, dlong, distance_km, fare

          var ul = document.getElementById("listParent");
          var lis = [];
          for(var i=0;i<near_by_rides.length;i++){
                var listViewItem=document.createElement('li');
                
                var ps = [];
                for(var q = 0; q < near_by_rides[i].length; q++){
                  item = near_by_rides[i][q];
                  var p = document.createElement('p');
                  const text = document.createTextNode(item);
                  p.appendChild(text);
                  ps.push(p);
                  console.log("Inside p",near_by_rides[i]);
                }
                console.log("bnm,.",ps);
                for(var c = 0; c < ps.length; c++){
                  console.log("Type:",ps[c]);
                  listViewItem.appendChild(ps[c]);
                }
                lis.push(listViewItem);
                // listViewItem.innerHTML = near_by_rides[i][0] + near_by_rides[i][1];
          }
          console.log("asdfghjkl:",lis);
          ul.appendChild(lis[0]);
          document.getElementById("responseText").innerHTML = "Got cha";

      }
  };

  // Converting JSON data to string
  var data = JSON.stringify({ 
    "pickup_latitude": pickup_latitude,
    "pickup_longitude": pickup_longitude,
    "dropoff_latitude": dropoff_latitude,
    "dropoff_longitude": dropoff_longitude,
    "passengers": passengers,
    "year": year,
    "month": month,
    "day": day,
    "hour": hour,
    "minute": minute,
    "weekday":weekday
   });

  // Sending data with the request
  xhr.send(data);

}

function ride_click(event){
  // all changes
  event.preventDefault();
  console.log("got here",event.target.value);
}



window.onload = (event) => {
  var date = new Date();
  var currentDate = date.toISOString().slice(0,10);
  var currentTime = date.getHours() + ':' + date.getMinutes();

  document.getElementById('date').value = currentDate;
  document.getElementById('time').value = currentTime;

  const form  = document.getElementById('submitFareForm');

  form.addEventListener('submit', (event) => {
    // stop form submission
    event.preventDefault();
    console.log("hey bro",event);
    
    submit();
  });

}