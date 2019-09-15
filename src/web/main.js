var table = document.getElementById("table");
var filesDiv = document.getElementById("filesDiv");
var ws;

function connect() {
    ws = new WebSocket("ws://" + location.hostname + "/ws");
    ws.onopen = function () {
        // subscribe to some channels
        console.log("WebSocket Open");
    };

    ws.onmessage = function (evt) {
        var json = JSON.parse(evt.data);
        if(typeof json["allowFiles"] !== 'undefined'){
            filesDiv.innerHTML = "";
            json["allowFiles"].forEach(element => {
                console.log(element);
                let a = document.createElement("a");
                let br = document.createElement("br");
                a.href = element;
                a.download = true;
                a.innerText = element.split("/")[2];
                filesDiv.appendChild(a);
                filesDiv.appendChild(br);
            });            
            return;
        }
        var keys = Object.keys(json);
        var row = table.insertRow(1);
        
        for (let i = 0; i < keys.length; i++) {
            var cell = row.insertCell(i);
            cell.innerText = json[keys[i]];
        }
        console.log(json);
    };

    ws.onclose = function (evt) {
        console.log('Socket is closed. Reconnect will be attempted in 1 second.', evt.reason);
        setTimeout(function () {
            connect();
        }, 1000);
    };

    ws.onerror = function (err) {
        console.error('Socket encountered error: ', err.message, 'Closing socket');
        ws.close();
    };
}

connect();