const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const PROTO_PATH = '../proto/RecognizeService.proto';
var packageDefinition = protoLoader.loadSync(
    PROTO_PATH,
    {
        keepCase: true,
        longs: String,
        enums: String,
        defaults: true,
        oneofs:true
    }
);

var protoDescriptor = grpc.loadPackageDefinition(packageDefinition);
var recognizeService = protoDescriptor.br.com.cpqd.asr.grpc;
const client = new recognizeService.RecognizeService('localhost:8026', grpc.credentials.createInsecure());

module.exports = client;