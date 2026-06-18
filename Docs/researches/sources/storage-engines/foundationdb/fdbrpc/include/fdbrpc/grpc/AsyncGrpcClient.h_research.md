## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/grpc/AsyncGrpcClient.h

Purpose: Provides a Flow-friendly asynchronous wrapper around generated gRPC service stubs when `FLOW_GRPC_ENABLED` is set.

Important APIs/types/functions: `AsyncGrpcClient<ServiceType>` stores an `AsyncTaskExecutor`, gRPC channel, and service stub. It defines RPC member-function pointer aliases for unary, server-streaming, and client-streaming calls. Constructors create insecure or credential-provider-backed channels. `call()` overloads support unary status-with-output, unary response-as-future, and server-streaming response streams.

Control flow: Calls assert they start on the Flow network thread, then post blocking gRPC operations to the executor. Unary calls create a `ThreadReturnPromise`, execute the stub method on a worker, and send either response/status or `grpc_error()`. Server-streaming calls read responses in a loop, cancel the gRPC context if the Flow stream is abandoned, and end with `end_of_stream()` or `grpc_error()`.

State and persistence behavior: Runtime state is the channel, stub, executor, and per-call promises. No durable state.

Dependencies and integration points: Depends on gRPC C++ headers, Flow thread promises, `AsyncTaskExecutor`, and `Credentials`. It bridges blocking gRPC APIs into Flow futures/streams for fdbrpc components that use gRPC.

Risks: Response pointers in the status-with-output overload must remain valid until the worker completes. The client captures `this` in posted work, so client lifetime must outlive in-flight calls. gRPC status details are collapsed to `grpc_error()` in some overloads. Blocking calls on too few executor threads can serialize work.

Test signals: Unary success/status failure, response pointer lifetime, abandoned future/stream behavior, server-streaming end-of-stream, gRPC cancellation, secure/insecure channel creation, and assertion that calls originate from the network thread.
