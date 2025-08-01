const express = require("express");
const http = require("http");
const WebSocket = require("ws");
const { PassThrough } = require("stream");
const PORT = process.env.PORT || 8080;
const client = require("./client-grpc"); // your gRPC client stub

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

wss.on("connection", function connection(ws) {
    const call = client.streamingRecognize();
    const stream = new PassThrough();
    console.log("Connected");

    call.on("data", (response) => {
        console.log("gRPC data");
        const result = response?.result?.[0];
        const alternative = result?.alternatives?.[0];
        const transcript = alternative?.text || alternative?.transcript;
        const start = String(result?.start_time).slice(0, 5)
        const end = String(result?.end_time).slice(0, 5)
        ans = transcript
        const diarization_result = result?.diarization_result;
        if (diarization_result)
          ans = `Spk: ${diarization_result.speaker} - [${start}-${end}]: ${transcript}`
        else
          ans = `Spk: unk - [${start}-${end}]: ${transcript}`

        if (transcript) {
            ws.send(`🗣️ ${ans}`);
        }
    });

    call.on("error", (err) => {
        ws.send("❌ gRPC error: " + err.message);
    });

    call.on("end", () => {
        ws.send("✅ gRPC stream ended");
    });

    call.write({
        config: {
            lm: [{
                uri: "builtin:slm/general",
                content_type: "text/uri-list"
            }],
            continuous_mode: "true",
            diarization_enabled: "true",
            audio_encoding: "WAV"
        }
    });

    ws.send("🎤 Recognition started");


    // Pipe audio to gRPC call
    stream.on("data", (chunk) => {
      //console.log("On data");
      call.write({ media: Uint8Array.from(chunk), last_packet: false }); 
    });

    ws.on("message", (data) => {
      //console.log("On message");
      stream.write(data);
    }); 

    ws.on("close", () => {
      console.log("Closed");
      stream.end();
      call.write({ media: Uint8Array.of(0), last_packet: true }); 
      call.end();
    }); 
});

app.use(express.static("public"));
server.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));
