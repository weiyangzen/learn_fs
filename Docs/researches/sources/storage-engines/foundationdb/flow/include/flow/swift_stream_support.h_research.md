# sources/storage-engines/foundationdb/flow/include/flow/swift_stream_support.h

## Purpose
This header bridges Flow `FutureStream<T>` callbacks to Swift checked continuations, with concrete support for `int` streams. It exists because Flow streams use `SingleCallback` rather than regular multi-callback futures.

## Important APIs, Types, and Functions
Aliases `PromiseStreamCInt` and `FutureStreamCInt` expose concrete stream types. Template `FlowSingleCallbackForSwiftContinuation<T>` derives from `SingleCallback<T>` and stores a `flow_swift::FlowCheckedContinuation<T>`. Concrete alias `FlowSingleCallbackForSwiftContinuation_CInt` binds it to `int`. `SwiftContinuationSingleCallbackCInt` is annotated `UNSAFE_SWIFT_CXX_IMMORTAL_REF`, derives from `SingleCallback<int>`, and exposes `make`, `addCallbackAndClearTo`, `fire`, `error`, and `unwait`.

## Control Flow
`FlowSingleCallbackForSwiftContinuation<T>::set` checks `this == thisPointer`, reconstructs a Swift continuation wrapper from an opaque pointer-sized value, stores it, and registers the callback with a `FutureStream<T>`. `fire` removes the callback, clears `next`, and resumes the continuation with either a const value or a copied rvalue. `error` removes and resumes throwing. The concrete `SwiftContinuationSingleCallbackCInt` stores raw Swift callback function pointers; its `fire` methods invoke `resumeWithValue`, and `error` logs the error then invokes `resumeWithError`.

## State and Persistence Behavior
State is callback-local and heap-local. `SwiftContinuationSingleCallbackCInt::make` allocates with `new` and the unsafe Swift immortal annotation means Swift will not retain/release in a normal ownership pattern. There is no persistence; lifetime correctness depends on Flow callback removal and external ownership expectations.

## Dependencies and Integration Points
It includes `swift.h`, `flow.h`, `unsafe_swift_compat.h`, `SwiftModules/Flow_CheckedContinuation.h`, pthreads, and integer headers. It integrates Flow `FutureStream`/`SingleCallback` with Swift continuations and generated Swift module glue.

## Risks
This is explicitly unsafe interop. The immortal reference annotation can leak or mask use-after-free. The raw `void*` continuation box and function pointers must remain valid until callback fire/error. `unwait()` is not implemented. `error()` prints to stdout using `printf` rather than Flow tracing and has special logging for end-of-stream. Private inheritance from `SingleCallback<T>` in the template may constrain how Swift/C++ sees the type.

## Test Signals
Tests should cover stream value delivery, end-of-stream error delivery, non-end errors, rvalue fire, callback removal, and object lifetime after `make`. Swift async tests should ensure continuations resume exactly once and that cancellation/unwait gaps are tracked.
