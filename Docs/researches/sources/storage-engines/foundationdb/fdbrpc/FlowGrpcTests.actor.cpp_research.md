# sources/storage-engines/foundationdb/fdbrpc/FlowGrpcTests.actor.cpp

## Purpose
`FlowGrpcTests.actor.cpp` contains actor-compiler style unit tests for the optional gRPC wrapper using synchronous wait syntax.

## Important APIs, Types, and Functions
It defines `forceLinkGrpcTests` and test cases `/fdbrpc/grpc/basic_sync_client`, `/fdbrpc/grpc/basic_async_client`, `/fdbrpc/grpc/actor_basic_stream_server`, `/fdbrpc/grpc/no_server_running`, and `/fdbrpc/grpc/destroy_server_without_shutdown`. It uses `GrpcServer`, `TestEchoServiceImpl`, `EchoClient`, `AsyncGrpcClient`, `AsyncTaskExecutor`, and generated echo service stubs.

## Control Flow
Tests start a `GrpcServer` on fixed localhost ports, register echo services, run the server actor, wait for `onRunning`, and issue sync or async RPCs. Streaming tests consume responses until `end_of_stream`. The no-server test verifies async RPC failure. The destroy-without-shutdown test leaves scope after starting a server to exercise destructor cleanup.

## State and Persistence Behavior
State is transient network listener state on localhost ports and in-memory service/client objects. No data is persisted.

## Dependencies and Integration Points
The file is compiled only under `FLOW_GRPC_ENABLED`, includes actor compiler support, Flow unit tests, `FlowGrpc.h`, and `FlowGrpcTests.h`. It validates integration between Flow actors/futures and gRPC client/server wrappers.

## Risks and Edge Cases
Fixed ports can collide with local processes or parallel test runs. Tests do not always explicitly shut down the server actor after success, relying on object lifetime or cancellation behavior. The actor stream test treats `end_of_stream` as the normal completion path.

## Test Signals
Passing tests show basic unary RPC, async client dispatch, server-stream consumption, expected failure with no listener, and server destructor cleanup work in actor syntax.
