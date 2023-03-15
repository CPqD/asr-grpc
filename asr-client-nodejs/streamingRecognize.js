const client = require("./client-grpc");
const fs = require("fs");

var call = client.streamingRecognize();

call.on("data", (response) => {
    console.log("data");
    console.log(response);
});

call.on("end", () => {
    console.log("end");
})

call.on("error", (err) => {
    console.log("error");
    console.error(err);
})

call.on("status", (status) => {
    console.log("status");
    console.log(status);
})

const configRequest = {
    config: {
        lm: [{
            uri: "builtin:slm/general",
            content_type: "text/uri-list"
        }],
        audio_encoding: "WAV"
    }
};

call.write(configRequest);

const readStream = fs.createReadStream("./cpf_8k.wav");
readStream.on("data", (chunk) => {
    call.write({
        media: Uint8Array.from(chunk),
        last_packet: false
    });
});
readStream.on("end", () => {
    call.write({
        media: Uint8Array.of(0),
        last_packet: true
    });

    call.end();
}); 