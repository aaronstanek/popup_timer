function PythonInput(message) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        PythonQuery();
    };
    xhttp.open("GET", "/input_"+message, true);
    xhttp.send();
}

function PythonInput_go() {
    var duration = document.getElementById("i").value;
    PythonInput("go_"+duration);
}

function PythonInput_pause() {
    PythonInput("pause");
}

function PythonInput_unpause() {
    PythonInput("unpause");
}

function PythonInput_stop() {
    PythonInput("stop");
}

function PythonQuery() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var s = JSON.parse( this.responseText );
            establishState(s);
        }
    };
    xhttp.open("GET", "/query", true);
    xhttp.send();
}

function setDisplay(vis) {
    document.getElementById("menu").style.display = "none";
    document.getElementById("running").style.display = "none";
    document.getElementById("pause").style.display = "none";
    document.getElementById("waiting").style.display = "none";
    document.getElementById(vis).style.display = "inline";
}

function establishState(s) {
    if (s["mode"] != STATE["mode"]) {
        setDisplay(s["mode"]);
        if (s["mode"] == "waiting") {
            if (s["value"]) {
                var h = window.screen.height;
                var w = window.screen.width;
                window.open('/popup', '_blank', 'height='+h+',width='+w+',menubar=0,status=0,toolbar=0', false);
            }
        }
    }
    STATE = s;
    if (s["mode"] == "running") {
        document.getElementById("tr").innerHTML = s["value"];
    }
    if (s["mode"] == "pause") {
        document.getElementById("tp").innerHTML = s["value"];
    }
}

function startMain() {
    setDisplay("menu");
    STATE = {"mode":"menu"};
    setInterval(PythonQuery,500);
}

function PythonAlive() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {};
    xhttp.open("GET", "/alive", true);
    xhttp.send();
}

function PopupButton() {
    CLICKCOUNT += 1;
    if (CLICKCOUNT >= 3) {
        window.close();
    }
    else {
        var b = document.getElementById("b");
        var c = b.getBoundingClientRect();
        b.style.position = "absolute";
        var left = window.innerWidth - c.width;
        left *= Math.random();
        b.style.left = left + "px";
        var top = window.innerHeight - c.height;
        top *= Math.random();
        b.style.top = top + "px";
    }
}

function startPopup() {
    setInterval(PythonAlive,500);
    CLICKCOUNT = -1;
    PopupButton();
}