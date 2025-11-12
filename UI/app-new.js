let mediaRecorder;
let audioChunks = [];
let ws;

const startBtn = document.getElementById('start-btn');
const stopBtn = document.getElementById('stop-btn');
const statusEl = document.getElementById('status');
const speakerEl = document.getElementById('speaker');
const transcriptEl = document.getElementById('transcript');
const responseEl = document.getElementById('response');

// Helper: Try best browser-supported audio format (Opus/webm preferred)
function getSupportedMimeType() {
    const possibleTypes = [
        'audio/webm;codecs=opus',
        'audio/webm',
        'audio/ogg;codecs=opus',
        'audio/ogg'
    ];
    return possibleTypes.find(type => MediaRecorder.isTypeSupported(type)) || '';
}

startBtn.addEventListener('click', async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mimeType = getSupportedMimeType();

        // Connect to your /voice WebSocket backend
        ws = new WebSocket('wss://c5e59a04153b.ngrok-free.app/voice');

        ws.onopen = () => {
            console.log('WebSocket connected');
            statusEl.textContent = 'Connected - Recording...';
            transcriptEl.textContent = '';
            responseEl.textContent = '';
        };

        ws.onmessage = async (event) => {
            if (typeof event.data === 'string') {
                transcriptEl.textContent = 'You: ' + event.data;
                speakerEl.textContent = 'You';
                if (event.data.startsWith('Bot reply:')) {
                    responseEl.textContent = event.data.replace('Bot reply:', '').trim();
                }
            } else {
                // Binary data from backend = bot response audio
                speakerEl.textContent = 'Bot';
                const audioBlob = new Blob([event.data], { type: 'audio/mpeg' });
                const audioUrl = URL.createObjectURL(audioBlob);
                const audio = new Audio(audioUrl);
                await audio.play();
                speakerEl.textContent = 'Idle';
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            statusEl.textContent = 'Error: ' + (error.message || error);
        };

        ws.onclose = () => {
            console.log('WebSocket closed');
            statusEl.textContent = 'Disconnected';
        };

        // Setup MediaRecorder
        audioChunks = [];
        mediaRecorder = new MediaRecorder(stream, { mimeType });

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
                console.log('Chunk collected:', event.data.size, 'Total chunks:', audioChunks.length);
            }
        };

        mediaRecorder.onstop = () => {
            // Combine all chunks into one blob and send
            const audioBlob = new Blob(audioChunks, { type: mimeType });
            console.log('Sending complete audio blob:', audioBlob.size, 'bytes');
            if (ws.readyState === WebSocket.OPEN && audioBlob.size > 0) {
                audioBlob.arrayBuffer().then(buffer => ws.send(buffer));
            }
            audioChunks = [];
        };

        // Start recording (no timeslice for best quality)
        mediaRecorder.start();
        startBtn.disabled = true;
        stopBtn.disabled = false;
        speakerEl.textContent = 'Recording...';
        statusEl.textContent = 'Recording - Speak Now';

    } catch (error) {
        console.error('Error starting:', error);
        statusEl.textContent = 'Error: ' + error.message;
    }
});

// Only send audio when STOP is pressed
stopBtn.addEventListener('click', () => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
    }
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close();
    }
    startBtn.disabled = false;
    stopBtn.disabled = true;
    statusEl.textContent = 'Stopped';
    speakerEl.textContent = 'Idle';
});
