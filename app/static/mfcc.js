function launch() {
    let constraintObj = {
        audio: true,
        video: false
    };

    navigator.mediaDevices.getUserMedia(constraintObj).then(mediaStreamObj => {
        let audio = document.getElementById('audio');
        if ('srcObject' in audio) {
            audio.srcObject = mediaStreamObj;
        }
        else {
            audio.src = window.URL.createObjectURL(mediaStreamObj);
        }
        audio.onloadedmetadata = (ev) => {
            audio.play();
        };

        /* globals Meyda */
        window.AudioContext = window.AudioContext || window.webkitAudioContext
        const audioContext = new AudioContext()
        const source = audioContext.createMediaStreamSource(mediaStreamObj);
        source.connect(audioContext.destination);
        let analyzer;


        let start = document.getElementById('btnStart');
        let stop = document.getElementById('btnStop');
        let mediaRecorder = new MediaRecorder(mediaStreamObj)
        console.debug(mediaStreamObj);
        let chunks = 0;
        data = [];
        let CONNECTION_PORT = 'http://localhost:5000'
        let socket = io.connect(CONNECTION_PORT);

        socket.on('recieve', function (msg) {
            console.log('RECIEVED : ', msg);
            $('#data').html(msg.proba)
        });

        start.addEventListener("click", (ev) => {
            mediaRecorder.start(1000);
            analyzer.start();
            {
                #analyzer.start();
                #
            }
            console.log('STARTED RECORDING with state : ', mediaRecorder.state);
        });

        stop.addEventListener("click", (ev) => {
            mediaRecorder.stop();
            analyzer.stop();
            console.log('STOPPED WITH DATA : ', data);
            data = [];
            {
                #analyzer.stop();
                #
            }
            console.log('STOPPED RECORDING with state : ', mediaRecorder.state);
        });

        mediaRecorder.ondataavailable = (ev) => {
            console.log("CURRENT DATA : ", data)
            socket.emit('json', data);
            chunks = ev.data;
            data = [];
        };

        mediaRecorder.onstop = (ev) => {
            {
                #let
                blob = new Blob(chunks, {'type': 'audio/wav'});
                #
            }
            chunks = 0;
            console.log('FULL STOP');
            analyzer.stop();
        };

        function show(features) {
            data.push(features['mfcc']);
        }

        if (typeof Meyda === "undefined") {
            console.log("Meyda could not be found. Have you included it?");
        }
        else {
            analyzer = Meyda.createMeydaAnalyzer({
                "audioContext": audioContext,
                "source": source,
                "bufferSize": 512,
                "featureExtractors": ["mfcc"],
                "callback": show
            });

        }

    }).catch((err) => {
        console.log(err.name, err.message);
    })
}