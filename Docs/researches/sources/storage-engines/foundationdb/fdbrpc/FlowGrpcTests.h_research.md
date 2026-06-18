# sources/storage-engines/foundationdb/fdbrpc/FlowGrpcTests.h

## Purpose
`FlowGrpcTests.h` defines the generated echo service test implementation and a small synchronous echo client used by gRPC unit tests.

## Important APIs, Types, and Functions
`TestEchoServiceImpl` implements `Echo`, `EchoRecvStream10`, and `EchoSendStream10` on `fdbrpc::test::TestEchoService::Service`. `EchoClient` wraps a generated stub and exposes `Echo`. The header aliases common gRPC and std types into `fdbrpc_test`.

## Control Flow
Unary `Echo` prefixes request messages with `"Echo: "`. Server-streaming `EchoRecvStream10` writes ten identical responses unless the context is cancelled. Client-streaming `EchoSendStream10` reads ten requests, concatenates messages, asserts count ten, and returns the concatenation. `EchoClient::Echo` performs a blocking unary RPC and returns either the response message or `"RPC failed"`.

## State and Persistence Behavior
The service is stateless beyond per-RPC locals. The client stores a generated stub. No data is persisted.

## Dependencies and Integration Points
The header is compiled only under `FLOW_GRPC_ENABLED` and depends on generated `fdbrpc/test/echo.grpc.pb.h`, gRPC C++ APIs, Flow errors/asserts, and test code in both gRPC test translation units.

## Risks and Edge Cases
Service methods use fixed counts and assertions, so malformed client-stream tests abort rather than return gRPC errors. `EchoClient` collapses all failures into a string, limiting diagnostics. `EchoRecvStream10` writes in a tight loop and only checks cancellation before each write.

## Test Signals
All gRPC test files use these helpers; passing tests validate generated stubs, service registration, unary RPCs, server streaming, and basic failure handling.
