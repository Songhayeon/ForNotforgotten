window.URL = window.URL ||
    window.webkitURL ||
    window.msURL ||
    window.mozURL;

// http://stackoverflow.com/questions/6524288
$.fn.pressEnter = function(fn) {

    return this.each(function() {
        $(this).bind('enterPress', fn);
        $(this).keyup(function(e) {
            if (e.keyCode == 13) {
                $(this).trigger("enterPress");
            }
        })
    });
};

function registerHbarsHelpers() {
    // http://stackoverflow.com/questions/8853396
    Handlebars.registerHelper('ifEq', function(v1, v2, options) {
        if (v1 === v2) {
            return options.fn(this);
        }
        return options.inverse(this);
    });
}

function sendFrameLoop() {
    if (socket == null || socket.readyState != socket.OPEN ||
        !vidReady || numNulls != defaultNumNulls) {
        return;
    }
    setTimeout(function() { requestAnimFrame(sendFrameLoop) }, 250);
}

function test(person_name, file_path) {
    alert("TEST");
    var msg = {
        'type': 'VIDEOCROP',
        'name': person_name,
        'path': file_path
    }
    socket.send(JSON.stringify(msg));
    alert("send video");

}

function train() {
    alert("train");
    var msg = {
        'type': 'TRAIN'
    }
    socket.send(JSON.stringify(msg));
    alert("send train");
}

function compare() {
    alert("COMPARE");
    var msg = {
        'type': 'COMPARE'
    }
    socket.send(JSON.stringify(msg));
    alert("send compare")
}

function updateRTT() {
    var diffs = [];
    for (var i = 5; i < defaultNumNulls; i++) {
        diffs.push(receivedTimes[i] - sentTimes[i]);
    }
    $("#rtt-" + socketName).html(
        jStat.mean(diffs).toFixed(2) + " ms (σ = " +
        jStat.stdev(diffs).toFixed(2) + ")"
    );
}

function sendState() {
    var msg = {
        'type': 'ALL_STATE',
        'images': images,
        'people': people,
        'training': training
    };
    socket.send(JSON.stringify(msg));
}

function insert_person(path, name, confi) {
    var temp = path.split("/");
    var img_source = temp[3] + "/" + temp[4] + "/" + temp[5];
    var img = "<img src='" + img_source + "' width= 50% height = 50%>";
	
    var person_name = "<h5>" + name + " " + confi + "</h5>";
    var return_str = "<td><div align=\"center\">" + person_name + img + "</div></td>";
    return return_str;
}

function createSocket(address, name) {
    socket = new WebSocket(address);
    socketName = name;
    socket.binaryType = "arraybuffer";
    socket.onopen = function() {
        $("#serverStatus").html("Connected to " + name);
        sentTimes = [];
        receivedTimes = [];
        tok = defaultTok;
        numNulls = 0

        socket.send(JSON.stringify({ 'type': 'NULL' }));
        sentTimes.push(new Date());
    }
    socket.onmessage = function(e) {
        console.log(e);
        j = JSON.parse(e.data)
        if (j.type == "NULL") {
            receivedTimes.push(new Date());
            numNulls++;
            if (numNulls == defaultNumNulls) {
                updateRTT();
                sendState();
                sendFrameLoop();
            } else {
                socket.send(JSON.stringify({ 'type': 'NULL' }));
                sentTimes.push(new Date());
            }
        } else if (j.type == "TRAIN_RETURN") {
            alert("TRAIN_RETURN");
        } else if (j.type == "COMPARE_RETURN") {
            $("table#content").append(insert_person(j.path, j.name, j.confidence));
        } else if (j.type == "VIDEO") {
            var temp = 'data:image/png;base64,' + j.data;
            document.getElementById('video').src = temp;
        } else {
            console.log("Unrecognized message type: " + j.type);
        }
    }
    socket.onerror = function(e) {
        console.log("Error creating WebSocket connection to " + address);
        console.log(e);
    }
    socket.onclose = function(e) {
        if (e.target == socket) {
            $("#serverStatus").html("Disconnected.");
        }
    }
}

function umSuccess(stream) {
    if (vid.mozCaptureStream) {
        vid.mozSrcObject = stream;
    } else {
        vid.src = (window.URL && window.URL.createObjectURL(stream)) ||
            stream;
    }
    vid.play();
    vidReady = true;
    sendFrameLoop();
}

function changeServerCallback() {
    $(this).addClass("active").siblings().removeClass("active");
    switch ($(this).html()) {
        case "Local":
            socket.close();
            redrawPeople();
            createSocket("wss:" + window.location.hostname + ":9000", "Local");
            break;
        case "CMU":
            socket.close();
            redrawPeople();
            createSocket("wss://facerec.cmusatyalab.org:9000", "CMU");
            break;
        case "AWS East":
            socket.close();
            redrawPeople();
            createSocket("wss://54.159.128.49:9000", "AWS-East");
            break;
        case "AWS West":
            socket.close();
            redrawPeople();
            createSocket("wss://54.188.234.61:9000", "AWS-West");
            break;
        default:
            alert("Unrecognized server: " + $(this.html()));
    }
}
