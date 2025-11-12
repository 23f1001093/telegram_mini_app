let ws;
let mediaRecorder;
let audioStream;
let statusEl, transcriptEl, responseEl, startBtn, stopBtn, speakerEl;
let audioContext;

document.addEventListener("DOMContentLoaded", () => {
    // UI refs
    startBtn = document.getElementById("start-btn");
    stopBtn = document.getElementById("stop-btn");
    statusEl = document.getElementById("status");
    transcriptEl = document.getElementById("transcript");
    responseEl = document.getElementById("response");
    speakerEl = document.getElementById("speaker");

    function resetUI() {
        statusEl.innerText = "Idle";
        transcriptEl.innerText = "";
        responseEl.innerText = "";
        speakerEl.innerText = "Idle";
        startBtn.disabled = false;
        stopBtn.disabled = true;
    }

    resetUI();

    // Start button handler
    startBtn.onclick = async () => {
        resetUI();
        statusEl.innerText = "Connecting...";
        startBtn.disabled = true;
        stopBtn.disabled = false;

        ws = new WebSocket("ws://localhost:8000/voice");
        ws.binaryType = "arraybuffer";

        audioContext = new (window.AudioContext || window.webkitAudioContext)();

        ws.onopen = async () => {
            statusEl.innerText = "Recording...";
            speakerEl.innerText = "You";

            try {
                audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(audioStream);

                mediaRecorder.ondataavailable = event => {
                    if (ws.readyState === WebSocket.OPEN) {
                        ws.send(event.data); // event.data: Blob (audio/wav or audio/webm)
                    }
                };

                mediaRecorder.start(250); // 250 ms chunk
            } catch (err) {
                statusEl.innerText = "Mic access denied";
                console.error("getUserMedia error:", err);
                resetUI();
                if (ws) ws.close();
            }
        };

        ws.onmessage = (msg) => {
            // Transcript: String, TTS reply: audio chunk
            if (typeof msg.data === "string") {
                transcriptEl.innerText = msg.data;
                speakerEl.innerText = "You";
            } else {
                speakerEl.innerText = "Bot";
                // Play audio chunk (MP3, WAV, whatever your server sends)
                audioContext.decodeAudioData(msg.data.slice(0), buffer => {
                    const source = audioContext.createBufferSource();
                    source.buffer = buffer;
                    source.connect(audioContext.destination);
                    source.start();
                }, err => {
                    console.error("decodeAudioData error:", err);
                });
            }
        };

        ws.onclose = () => {
            statusEl.innerText = "Call ended";
            speakerEl.innerText = "Idle";
            resetUI();
        };

        ws.onerror = (err) => {
            statusEl.innerText = "Connection error";
            console.error(err);
            resetUI();
        };
    };

    // Stop button handler
    stopBtn.onclick = () => {
        if (mediaRecorder && mediaRecorder.state !== "inactive") {
            mediaRecorder.stop();
        }
        if (audioStream) {
            audioStream.getTracks().forEach(track => track.stop());
        }
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.close();
        }
        statusEl.innerText = "Processing...";
        stopBtn.disabled = true;
        startBtn.disabled = false;
    };
});
