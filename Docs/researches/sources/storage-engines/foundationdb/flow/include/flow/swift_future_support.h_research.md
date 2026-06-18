# sources/storage-engines/foundationdb/flow/include/flow/swift_future_support.h

## Purpose
This header supplies Swift-friendly aliases for Flow `Promise`, `Future`, `Callback`, `PromiseStream`, and `FutureStream` template instantiations. It is part of the bridge that lets Swift code work with concrete Flow future types despite limited direct template interop.

## Important APIs, Types, and Functions
Aliases include `PromiseCInt`, `FutureCInt`, `CallbackInt`, `PromiseVoid`, `FutureVoid`, `CallbackVoid`, `PromiseStreamCInt`, `FutureStreamCInt`, `PromiseStreamVoid`, `FutureStreamVoid`, `PromiseStreamFutureVoid`, and `FutureStreamFutureVoid`. It also aliases `FlowCallbackForSwiftContinuationCInt` and `FlowCallbackForSwiftContinuationVoid` to `FlowCallbackForSwiftContinuation<int>` and `FlowCallbackForSwiftContinuation<Void>`.

## Control Flow
The large `FlowCallbackForSwiftContinuation` implementation is commented out, documenting the intended bridge: validate Swift did not copy the callback object, reinterpret a Swift checked-continuation handle passed through `void*`, register with a `Future`, then resume or throw from `fire`/`error`. Active control flow is limited to type alias exposure.

## State and Persistence Behavior
The header itself stores no state. The intended callback bridge would own a Swift continuation wrapper and mutate Flow callback links, but that implementation is not active in this file. The exposed aliases represent runtime future/promise state owned by Flow objects.

## Dependencies and Integration Points
It includes `swift.h`, `flow.h`, `swift_stream_support.h`, `unsafe_swift_compat.h`, `SwiftModules/Flow_CheckedContinuation.h`, pthreads, and integer headers. It depends on `FlowCallbackForSwiftContinuation` being defined elsewhere or generated so the aliases compile.

## Risks
The file is sensitive to Swift/C++ template interop limitations and generated module availability. If `FlowCallbackForSwiftContinuation` is not visible before these aliases are used, builds will fail. The commented bridge shows unsafe `void*` reinterpretation and lifetime assumptions that can cause use-after-free or continuation misuse if revived incorrectly.

## Test Signals
Swift build tests should import the aliases and await `Future<int>`/`Future<Void>` through the intended bridge. Runtime tests should cover successful values, thrown `Error`, cancellation/unwait behavior once implemented, and callback object lifetime across Swift/C++ boundaries.
