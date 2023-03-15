const client = require("./client-grpc");
const fs = require("fs");

var data = fs.readFileSync("./cpf_8k.wav");

const request = {
    config: {
        lm: [{
            uri: "builtin:slm/general",
            content_type: "text/uri-list"
        }],
        audio_encoding: "WAV"
    },
    media: Uint8Array.from(data)
};

client.recognize(request, (err, response) => {
    if(err){
        console.error(err);
    }else{
        console.log(response.result);
    }
});