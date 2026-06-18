# sources/storage-engines/foundationdb/fdbserver/include/fdbserver/NetworkTest.h

## Purpose
Declares RPC messages, interface streams, and client/server entrypoints for FoundationDB network testing.

## Important APIs, Types, and Functions
- `NetworkTestInterface` exposes unary and streaming request streams and constructors for remote/local endpoints.
- `NetworkTestRequest` carries a key, requested reply size, and reply promise.
- `NetworkTestReply` carries a value payload.
- `NetworkTestStreamingRequest` carries a reply promise stream.
- `NetworkTestStreamingReply` carries stream ack/sequence fields and an index; `expectedSize()` advertises a large reply.
- `networkTestServer()` and `networkTestClient(...)` are actor entrypoints.

## Control Flow
`fdbserver.cpp` dispatches network test roles to these entrypoints. The interface supports both unary request/reply and streaming replies.

## State and Persistence Behavior
Messages are transient RPC payloads with no persistence.

## Dependencies and Integration Points
Depends on FDB types, fdbrpc streams, Flow file identifiers, and `INetwork`. Integrates with executable role dispatch and transport serialization.

## Risks and Edge Cases
Serialization `FileIdentifier`s must remain stable. Large `expectedSize()` can stress transport buffering/memory. Constructors are declared elsewhere.

## Test Signals
Network test roles are the runtime validation path.
