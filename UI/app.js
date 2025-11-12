let mediaRecorder;
let audioChunks = [];
let ws;
let recordingInterval;

const startBtn = document.getElementById('start-btn');
const stopBtn = document.getElementById('stop-btn');
const statusEl = document.getElementById('status');
const speakerEl = document.getElementById('speaker');
const transcriptEl = document.getElementById('transcript');
const responseEl = document.getElementById('response');

startBtn.addEventListener('click', async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        // Connect WebSocket
        ws = new WebSocket('https://d9f3d5cba441.ngrok-free.app');
        
        ws.onopen = () => {
            console.log('WebSocket connected');
            statusEl.textContent = 'Connected - Recording...';
        };
        
        ws.onmessage = async (event) => {
            if (typeof event.data === 'string') {
                // Text message = transcript
                transcriptEl.textContent = 'You: ' + event.data;
                speakerEl.textContent = 'You';
            } else {
                // Binary data = audio from bot
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
            statusEl.textContent = 'Error: ' + error.message;
        };
        
        ws.onclose = () => {
            console.log('WebSocket closed');
            statusEl.textContent = 'Disconnected';
        };
        
        // Setup MediaRecorder
        audioChunks = [];
        mediaRecorder = new MediaRecorder(stream);
        
        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
                console.log('Chunk collected:', event.data.size, 'Total chunks:', audioChunks.length);
            }
        };
        
        mediaRecorder.onstop = () => {
            // Combine all chunks into one blob
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            console.log('Sending complete audio blob:', audioBlob.size, 'bytes');
            
            if (ws.readyState === WebSocket.OPEN && audioBlob.size > 0) {
                audioBlob.arrayBuffer().then(buffer => {
                    ws.send(buffer);
                });
            }
            
            // Clear for next recording
            audioChunks = [];
        };
        
        // Start recording with timeslice to collect chunks
        mediaRecorder.start(1000); // Collect data every 1 second
        
        // Stop and restart every 3 seconds to send complete audio
        recordingInterval = setInterval(() => {
            if (mediaRecorder && mediaRecorder.state === 'recording') {
                mediaRecorder.stop();
                // Restart after a brief pause
                setTimeout(() => {
                    if (mediaRecorder && mediaRecorder.stream.active) {
                        audioChunks = [];
                        mediaRecorder.start(1000);
                    }
                }, 200);
            }
        }, 3000);
        
        startBtn.disabled = true;
        stopBtn.disabled = false;
        speakerEl.textContent = 'Recording...';
        
    } catch (error) {
        console.error('Error starting:', error);
        statusEl.textContent = 'Error: ' + error.message;
    }
});

stopBtn.addEventListener('click', () => {
    if (recordingInterval) {
        clearInterval(recordingInterval);
    }
    
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
    }
    
    if (ws) {
        ws.close();
    }
    
    startBtn.disabled = false;
    stopBtn.disabled = true;
    statusEl.textContent = 'Stopped';
    speakerEl.textContent = 'Idle';
});
