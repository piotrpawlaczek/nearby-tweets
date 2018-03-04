var map = L.map('map').setView([53.3498050, -6.2603100], 13);

L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);


var markerGroup = L.layerGroup().addTo(map);
var query_params = window.location.search.slice(1);
var ws = new WebSocket('ws://' + document.domain + ':' + location.port + '/feed?on_map=true&' + query_params);

ws.onmessage = function (event) {
	markerGroup.clearLayers();
	var data = JSON.parse(event.data);
	map.setView(data.geometry.coordinates, 13); 
	L.marker(data.geometry.coordinates).addTo(markerGroup).bindPopup(data.tweet).openPopup();
};

