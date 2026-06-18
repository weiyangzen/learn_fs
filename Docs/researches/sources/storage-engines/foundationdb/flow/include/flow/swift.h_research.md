# sources/storage-engines/foundationdb/flow/include/flow/swift.h

## Purpose
This is a compact umbrella header for Flow's Swift interop surface. It pulls in Swift support annotations, Swift ABI task definitions, and Flow protocol-version context, then declares small C++ APIs Swift code can call to interact with the Flow network.

## Important APIs, Types, and Functions
The header includes `swift_support.h`, `swift/ABI/Task.h`, and `flow/ProtocolVersion.h`. It declares `_tid()` as an inline wrapper around `pthread_self()`, `flow_gNetwork_now()`, `flow_gNetwork_delay(double seconds, TaskPriority taskID)`, `JobDelay` as nanoseconds, and `ExecutorRef` with `Identity`, `Implementation`, and `ExecutorRef::generic()`.

## Control Flow
The only implemented control flow is `_tid()` returning the current pthread id and `ExecutorRef::generic()` constructing a null identity/zero implementation executor. The Flow network functions are declarations whose behavior is supplied by implementation files. Swift concurrency hook code later uses `ExecutorRef` when running Swift jobs on a generic executor.

## State and Persistence Behavior
No persistent state is stored. `ExecutorRef` is a by-value ABI carrier for Swift executor identity/implementation bits. `flow_gNetwork_*` declarations imply access to global Flow network state, but this header does not own it.

## Dependencies and Integration Points
This header is an integration point between Flow futures/networking, Swift ABI job structures, and Swift-generated code. It depends on pthreads transitively for `_tid`, Swift ABI declarations, and Flow `Future<Void>`/`TaskPriority` declarations from included headers.

## Risks
The header is ABI-facing: changing `ExecutorRef` layout or function signatures can break Swift/C++ interop. `TaskPriority` is forward-declared as an enum class and must match included Flow definitions in translation units. Because `Future<class Void>` appears in a declaration, include ordering must provide compatible Flow future declarations before use in implementation.

## Test Signals
Swift-enabled builds should compile generated Swift module headers that include this file. Runtime smoke tests should call `flow_gNetwork_now`, await `flow_gNetwork_delay`, and run jobs with `ExecutorRef::generic()` through the hook layer.
