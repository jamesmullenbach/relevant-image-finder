var url = "http://compjproj.herokuapp.com/?text=";
var xmlhttp = new XMLHttpRequest();
document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('generateButton').addEventListener('click', getImages);
});

xmlhttp.onreadystatechange = function() {
    if (xmlhttp.readyState <= 1) {
        document.getElementById('mainArea').innerHTML = "loading images (may take a few seconds)";
    } else { //it's past initialization
        if (xmlhttp.responseText) {
            var myArr = JSON.parse(xmlhttp.responseText);
            if (myArr && myArr.results && myArr.results.length > 0) {
                displayImages(myArr);
            } else {
                document.getElementById('mainArea').innerHTML = "No named entities were recognized.";
            }
        } else {
            document.getElementById('mainArea').innerHTML = "An error occurred. Please try again or use another body of text."
        }
    }
}

function getImages(){
	var fromTextBox = document.getElementById("textBox").value;
	fromTextBox = encodeURIComponent(fromTextBox.trim());
	url += fromTextBox;
    var genButton = document.getElementById('generateButton');
    genButton.innerHTML = "Generated";
    //document.getElementById('mainArea').innerHTML =
    //	'<object type="text/html" data="results.html" ></object>';

	document.getElementById('mainArea').innerHTML = "loading images (may take a few seconds)";

	xmlhttp.open("GET", url, true);
	xmlhttp.send();

}

function displayImages(myArr) {
    document.getElementById('mainArea').innerHTML = "";
    for(var i = 0; i < myArr.results.length; i++) //goes through each entity
    {
        document.getElementById("mainArea").innerHTML += "<font size = 20>" + (myArr.results[i].entity) + "</font><br>";
        for (var j = 0; j < myArr.results[i].urls.length; j++) {
            //document.getElementById("mainArea").innerHTML += (myArr.results[i].urls[j]) + "<br>";
            if(myArr.results[i].urls[j] != "n/a") {
                var elem = document.createElement("img");
                elem.src = myArr.results[i].urls[j];
                elem.width = 350;
                document.getElementById("mainArea").appendChild(elem);
            }
        }
    }
}
