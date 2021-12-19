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
      $('#currloc').html(city);
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
      $('#temp').html(temp.toFixed(2) + " °C");
      $('#humi').html(data.main.humidity + "%");
      $('#wind').html((data.wind.speed * 3.6).toFixed(2) + " Km/Hr");
      $('#cond').html(data.weather[0].description);
    }
  });
}

fetchLocationName()
