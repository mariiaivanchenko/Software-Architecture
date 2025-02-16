import grpc
from concurrent import futures
import micro_basics_pb2
import micro_basics_pb2_grpc


class LoggingService(micro_basics_pb2_grpc.LoggingService):

    def __init__(self):
        self.db = {}

    def Get(self, request, context):
        return micro_basics_pb2.Messages(messages=list(self.db.values()))

    def Post(self, request, context):
        message = request.message
        if message not in self.db.values():
            self.db[request.uuid] = message
        return micro_basics_pb2.Response(message=message, status_code=200)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    micro_basics_pb2_grpc.add_LoggingServiceServicer_to_server(
        LoggingService(), server
    )
    server.add_insecure_port("[::]:5001")
    server.start()
    print("Logging Service gRPC server running on port 5001...")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
