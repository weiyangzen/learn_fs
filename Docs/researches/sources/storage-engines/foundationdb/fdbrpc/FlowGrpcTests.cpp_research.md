# sources/storage-engines/foundationdb/fdbrpc/FlowGrpcTests.cpp

## Purpose
`FlowGrpcTests.cpp` provides coroutine-style tests for gRPC clients/servers, file transfer, async task execution, server lifecycle restarts, and TLS/mTLS credentials.

## Important APIs, Types, and Functions
Helpers include `generate_random_string`, `WriteTestFile`, and `GPRC_FILE_TRANSFER_TEST_FILE_SIZE`. Test cases cover `/fdbrpc/grpc/basic_coro`, `/basic_stream_server`, `/future_destroy`, `/stream_destroy`, `/file_transfer`, `/file_transfer_byte_flip`, `/file_transfer_fail_random`, `/basic_thread_pool`, `/server_lifecycle_basic`, `/server_lifecycle_combine_register_into_one_start`, and `/basic_tls`.

## Control Flow
The basic tests start a `GrpcServer`, register echo services, create `AsyncGrpcClient`, and await unary or streaming responses. Lifetime tests drop futures or streams early. File-transfer tests create temporary source/destination files, start a raw gRPC server with `FileTransferServiceImpl`, run downloads, and assert success or expected failure under byte-flip/random-failure injection. Thread-pool tests post void and value-returning lambdas and verify errors propagate. Lifecycle tests register/deregister services and observe server restart counts. TLS tests create static credential providers and verify insecure, correct, incorrect, and different-root client behaviors.

## State and Persistence Behavior
State is transient: localhost server sockets, temporary files, generated random file contents, test TLS certificate strings, service registry state, and thread-pool work queues. Temporary files are destroyed in file-transfer tests after assertions.

## Dependencies and Integration Points
The file depends on `FlowGrpc.h`, `FlowGrpcTests.h`, `FileTransfer.h`, Flow unit tests, TLS config, deterministic randomness, gRPC C++ APIs, and platform temp files. It is active only with `FLOW_GRPC_ENABLED`.

## Risks and Edge Cases
Fixed localhost ports can conflict. File-transfer tests use large 40 MiB temp files and comments mention 1 GiB despite the constant, which can confuse diagnostics. TLS certificates are embedded static material with long validity and are not regenerated. Some server actors are not explicitly awaited for shutdown. The tests may expose the `stopServerSyncInternal` shutdown bug if destructor/sync paths are exercised strictly.

## Test Signals
These tests are the strongest signals for fdbrpc gRPC: unary calls, streaming end-of-stream, future/stream destruction, file integrity checks, failure cleanup, thread-pool error forwarding, service restart behavior, and TLS credential enforcement.
