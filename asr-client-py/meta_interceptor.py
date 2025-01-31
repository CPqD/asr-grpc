import grpc


class MetaInterceptor(grpc.UnaryUnaryClientInterceptor, grpc.StreamStreamClientInterceptor):
    def __init__(self, token, meta):
        self.token = token
        self.meta = meta

    def get_metadata(self):
        metadata=()
        if self.meta:
            meta_par=self.meta[0:self.meta.find(':')]
            meta_val=self.meta[self.meta.find(':')+1:]
            metadata = metadata + ((meta_par, meta_val),)
        if self.token:
            metadata = metadata + (('authorization', 'Bearer ' + self.token),)
        return metadata

    def intercept_unary_unary(self, continuation, client_call_details, request):
        new_details = CustomClientCallDetails(client_call_details, self.get_metadata())
        return continuation(new_details, request)

    def intercept_stream_stream(self, continuation, client_call_details, request_iterator):
        new_details = CustomClientCallDetails(client_call_details, self.get_metadata())
        return continuation(new_details, request_iterator)


class CustomClientCallDetails(grpc.ClientCallDetails):
    def __init__(self, client_call_details, metadata):
        self.method = client_call_details.method
        self.timeout = client_call_details.timeout
        self.metadata = metadata
        self.credentials = client_call_details.credentials
