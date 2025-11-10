    let socket, audioContext, processorNode;
    let canvasCtx, waveformCanvas;
    let WS_PORT = 8080
    const sampleRate = 8000;
    const durationSec = 40; // Show last 1 second
    const maxSamples = sampleRate * durationSec;
    let sampleBuffer = new Float32Array(maxSamples);

    async function loadConfig() {
      console.log(WS_PORT);
      const response = await fetch('/config.json');
      const config = await response.json();
      console.log(config.WS_PORT);
      WS_PORT = config.WS_PORT
      console.log(WS_PORT);
    }

    function setupCanvas() {
      waveformCanvas = document.getElementById("waveform");
      waveformCanvas.width = 1800;
      waveformCanvas.height = 200;
      canvasCtx = waveformCanvas.getContext("2d");
      // Clear the canvas before starting
      canvasCtx.clearRect(0, 0, waveformCanvas.width, waveformCanvas.height);
      canvasCtx.fillStyle = 'black';
      canvasCtx.fillRect(0, 0, waveformCanvas.width, waveformCanvas.height);
      sampleBuffer.fill(0);
      canvasCtx.lineWidth = 2;
      // canvasCtx.strokeStyle = "#007acc"; // blue
      canvasCtx.strokeStyle = "#00cc00";
    }


    function drawWaveform(samples) {
      const width = waveformCanvas.width;
      const height = waveformCanvas.height;
      const centerY = height / 2;

      // canvasCtx.clearRect(0, 0, width, height);
      canvasCtx.fillStyle = 'black';
      canvasCtx.fillRect(0, 0, waveformCanvas.width, waveformCanvas.height)
      canvasCtx.beginPath();

      const step = Math.max(1, Math.floor(samples.length / width));

      for (let x = 0; x < width; x++) {
        const i = x * step;
        const sample = samples[i] || 0;
        const y = centerY + sample * centerY;
        if (x === 0) canvasCtx.moveTo(x, y);
        else canvasCtx.lineTo(x, y);
      }

      canvasCtx.stroke();

    }

    function updateWaveform(newSamples) {
      const newLength = newSamples.length;

      // Shift buffer to the left, drop old samples
      sampleBuffer.set(sampleBuffer.subarray(newLength));
      sampleBuffer.set(newSamples, sampleBuffer.length - newLength);

      // Draw updated waveform
      drawWaveform(sampleBuffer);
    }

    async function start() {
      setupCanvas();
      const output = document.getElementById("output");
      output.textContent = "";

      socket = new WebSocket(`ws://localhost:${WS_PORT}`);
      output.textContent = `✅ WebSocket conectado ${WS_PORT}\n`;

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioContext = new AudioContext({ sampleRate: 16000 });

      await audioContext.audioWorklet.addModule('worklet.js');
      processorNode = new AudioWorkletNode(audioContext, 'pcm-worklet');

      processorNode.port.onmessage = e => {
        const msg = e.data;

        if (msg.type === "pcm" && socket.readyState === WebSocket.OPEN) {
          socket.send(msg.data);
        } else if (msg.type === "raw") {
          const floatSamples = new Float32Array(msg.data);
          updateWaveform(floatSamples);
        }
      };

      const source = audioContext.createMediaStreamSource(stream);
      source.connect(processorNode).connect(audioContext.destination);

      socket.onmessage = (msg) => {
        output.textContent += msg.data + "\n";
      };
    }

    function stop() {
      if (processorNode) processorNode.disconnect();
      if (audioContext) audioContext.close();
      if (socket && socket.readyState === WebSocket.OPEN) socket.close();
      output.textContent += "🛑 Conexão encerrada\n";
    }
    loadConfig();
