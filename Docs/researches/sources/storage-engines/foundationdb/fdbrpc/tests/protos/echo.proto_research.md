# sources/storage-engines/foundationdb/fdbrpc/tests/protos/echo.proto

## Purpose
`echo.proto` defines a small gRPC echo service for fdbrpc tests. It supplies unary, server-streaming, and client-streaming echo RPC shapes over simple string request/response messages.

## Important APIs, Types, And Functions
The proto uses `syntax = "proto3"` and package `fdbrpc.test`. `TestEchoService` exposes `Echo(EchoRequest) returns (EchoResponse)`, `EchoRecvStream10(EchoRequest) returns (stream EchoResponse)`, and `EchoSendStream10(stream EchoRequest) returns (EchoResponse)`. `EchoRequest` and `EchoResponse` each contain `string message = 1`.

## Control Flow
There is no executable control flow in the proto. When `WITH_GRPC` is enabled, CMake invokes `generate_grpc_protobuf(fdbrpc.test protos/echo.proto)`, producing generated service and message code for tests.

## State And Persistence Behavior
The schema has no persistent storage. The only state carried on the wire is the `message` string in request and response messages.

## Dependencies And Integration Points
The file integrates with protobuf/gRPC tooling through `fdbrpc/tests/CMakeLists.txt`. Its package name determines generated namespaces/packages for test code. The method names indicate coverage for unary calls and both streaming directions.

## Risks And Test Signals
Changing field numbers or package names would break generated-code compatibility. The `RecvStream10` and `SendStream10` names encode an expected count in the method name, but the schema itself does not enforce a count of 10; test implementations must do that. Builds with `WITH_GRPC=ON` should generate and compile protobuf/gRPC artifacts and runtime tests should exercise unary, receive-streaming, and send-streaming echo semantics.
