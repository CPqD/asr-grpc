  let ws, mediaRecorder, stream;
  let audioCtx, analyser, dataArray, animationId;

  const canvas = document.getElementById("waveform");
  const ctx = canvas.getContext("2d");
  const output = document.getElementById("output");

  async function startStream() {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    output.textContent += "🔊 Mic started\n";

    // Set up WebSocket
    ws = new WebSocket("ws://localhost:8080");

    ws.onopen = () => {
      mediaRecorder = new MediaRecorder(stream, {
        mimeType: "audio/webm;codecs=opus"
      });

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0 && ws.readyState === WebSocket.OPEN) {
          ws.send(e.data);
        }
      };

      mediaRecorder.start(250); // send every 250ms
    };

    ws.onmessage = (msg) => {
      output.textContent += msg.data + "\n";
    };

    ws.onerror = (err) => {
      console.error("WebSocket error", err);
      output.textContent += "WebSocket error\n";
    };

    ws.onclose = () => {
      output.textContent += "WebSocket closed\n";
    };

    // Set up AudioContext for waveform
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const source = audioCtx.createMediaStreamSource(stream);
    analyser = audioCtx.createAnalyser();
    analyser.fftSize = 2048;

    const bufferLength = analyser.fftSize;
    dataArray = new Uint8Array(bufferLength);

    source.connect(analyser);
    draw(); // Start waveform animation
  }

  function draw() {
    animationId = requestAnimationFrame(draw);

    analyser.getByteTimeDomainData(dataArray);

    ctx.fillStyle = "black";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.lineWidth = 2;
    ctx.strokeStyle = "lime";

    ctx.beginPath();

    const sliceWidth = canvas.width / dataArray.length;
    let x = 0;

    for (let i = 0; i < dataArray.length; i++) {
      const v = dataArray[i] / 128.0;
      const y = (v * canvas.height) / 2;

      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }

      x += sliceWidth;
    }

    ctx.lineTo(canvas.width, canvas.height / 2);
    ctx.stroke();
  }

  function stopStream() {
    if (mediaRecorder) {
      mediaRecorder.stop();
      mediaRecorder = null;
    }

    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      stream = null;
    }

    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.close();
    }

    if (audioCtx) {
      audioCtx.close();
    }

    if (animationId) {
      cancelAnimationFrame(animationId);
    }

    output.textContent += "🛑 Mic stopped\n";
  }