let ws;
let mediaRecorder;
let stream;
let audioBuffers = [];
let partialTranscript = "";

document.addEventListener("DOMContentLoaded", () => {
    const startBtn = document.getElementById("start-btn");
    const stopBtn = document.getElementById("stop-btn");
    const statusEl = document.getElementById("status");
    const transcriptEl = document.getElementById("transcript");
    const responseEl = document.getElementById("response");

    function resetUI() {
        statusEl.innerText = "Idle";
        transcriptEl.innerText = "";
        responseEl.innerText = "";
        audioBuffers = [];
        partialTranscript = "";
        startBtn.disabled = false;
        stopBtn.disabled = true;
    }

    resetUI();

    startBtn.onclick = async () => {
        resetUI();
        statusEl.innerText = "Connecting...";
        startBtn.disabled = true;
        stopBtn.disabled = false;
        ws = new WebSocket("ws://localhost:8000/voice");
        ws.binaryType = "arraybuffer";

        ws.onopen = async () => {
            statusEl.innerText = "Recording...";
            try {
                stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);

                mediaRecorder.ondataavailable = event => {
                    if (ws.readyState === WebSocket.OPEN) {
                        ws.send(event.data);
                    }
                };

                mediaRecorder.start(250); // send every 250ms
            } catch (err) {
                statusEl.innerText = "Microphone access denied or error";
                console.error("getUserMedia error:", err);
                resetUI();
                ws.close();
            }
        };

        ws.onmessage = (msg) => {
            if (typeof msg.data === "string") {
                partialTranscript = msg.data;
                transcriptEl.innerText = partialTranscript;
                console.log("Received partial transcript:", partialTranscript);
            } else {
                audioBuffers.push(msg.data);
                console.log("Received audio chunk, size:", msg.data.byteLength);
            }
        };

        ws.onclose = () => {
            statusEl.innerText = "Bot replying...";
            responseEl.innerText = partialTranscript;

        if (audioBuffers.length > 0) {
           const audioBlob = new Blob(audioBuffers, { type: "audio/mpeg" }); // match backend!
           const audio = new Audio(URL.createObjectURL(audioBlob));
           audio.play();
        } else {
            statusEl.innerText = "No audio reply received";
            resetUI();
        }
        };

        ws.onerror = (err) => {
            statusEl.innerText = "Connection error";
            console.error(err);
            resetUI();
        };
    };

    stopBtn.onclick = () => {
        if (mediaRecorder && mediaRecorder.state !== "inactive") {
            mediaRecorder.stop();
        }
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.close();
        }
        statusEl.innerText = "Processing...";
        stopBtn.disabled = true;
        startBtn.disabled = false;
    };
});