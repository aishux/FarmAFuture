
// manage cross erasing input values
var clears = document.querySelectorAll(".clear");
var inputs = document.querySelectorAll("input");

for (let i=0; i<3; i++) {
  inputs[i].addEventListener("input", function(e) {
    if (e.target.value.length > 0) {
      clears[i].style.display = "block";
    }
    else {
      clears[i].style.display = "none";
    }
  });

  clears[i].addEventListener("click", function() {
    inputs[i].value = "";
    this.style.display = "none";
  });
}

var city
var state
function fetchLocationName(){
  $.ajax({
    url: "https://geolocation-db.com/jsonp",
    jsonpCallback: "callback",
    dataType: "jsonp",
    success: function(location) {
      city = location.city
      state = location.state
      getWeatherDetails()
    }
  });
}

function getWeatherDetails(){
  $.ajax({
    url: "https://api.openweathermap.org/data/2.5/weather?q="+city+"&appid=2e8e57b6aadeffe86777fa7c2a261216",
    dataType: "json",
    success: function(data) {
      var temp = data.main.temp - 273.1
      $('#temperature').val(temp.toFixed(2));
      $('#humidity').val(data.main.humidity);
    }
  });
}

fetchLocationName()