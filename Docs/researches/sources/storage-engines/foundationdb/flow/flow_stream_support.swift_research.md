# sources/storage-engines/foundationdb/flow/flow_stream_support.swift

Purpose: adds Swift async stream protocol conformances for Flow `FutureStream` bridge types.

Important APIs/types/functions: extension `FutureStreamCInt: FlowStreamOps` and extension `FlowSingleCallbackForSwiftContinuation_CInt: FlowSingleCallbackForSwiftContinuationProtocol`; associated types `Element`, `SingleCB`, and `AsyncIterator`.

Control flow: no runtime logic in this file; it wires generated Flow C++ interop types into generic Swift stream machinery.

State/persistence: no state.

Dependencies/integration: imports `Flow` and depends on protocol definitions from the Swift support layer. Commented-out Void stream conformance indicates planned or blocked additional coverage.

Risks: currently only active for `CInt`; other element types need explicit conformance. Type names are generated/interop-sensitive.

Test signals: Swift async iteration over `FutureStreamCInt` should compile and use `FlowStreamOpsAsyncIteratorAsyncIterator`.
