# sources/storage-engines/foundationdb/flow/stream_support.swift

## Purpose
This Swift file adapts Flow `FutureStream`-style types to Swift `AsyncSequence` and `AsyncIteratorProtocol`. It provides generic protocols and a default iterator implementation so generated Swift interop wrappers can be consumed with `for await` and `await stream.waitNext`.

## Important APIs, Types, And Functions
`FlowStreamOpsAsyncIterator` constrains iterator `Element` to its associated stream element and requires `init(_:)`. `FlowSingleCallbackForSwiftContinuationProtocol` models a C++ `SingleCallback<T>` bridge with `init()` and `set(_ continuationPointer, _ stream, _ thisPointer)`. `FlowStreamOps` is the main protocol, requiring `Element`, `SingleCB`, `waitNext`, `makeAsyncIterator`, `isReady`, `isError`, `pop`, and `getError`. The extension implements `waitNext` and `makeAsyncIterator`. `FlowStreamOpsAsyncIteratorAsyncIterator` stores the stream and implements `next()`.

## Control Flow
`waitNext` first checks `isReady()`. If ready and in error state, it returns `nil` for `end_of_stream` or throws `GeneralFlowError`; if ready with a value, it pops and returns the element. If not ready, it creates a single callback and a `CheckedContinuation`, wraps the continuation in `FlowCheckedContinuation`, passes pointers for the continuation, stream, and callback object into `SingleCB.set`, and resumes later from the C++ callback path. The iterator simply delegates `next()` to `stream.waitNext`.

## State And Persistence
State is held in the conforming stream object and in the iterator's `stream` property. During suspension, state is split across the Swift continuation wrapper and the C++ callback registered through `SingleCB.set`. There is no file-global persistent state.

## Dependencies And Integration Points
The file imports `Flow` and relies on generated C++ interop types for `Flow.Error`, `GeneralFlowError`, `FlowCheckedContinuation`, stream wrappers, and `SingleCallback` wrappers. It is the user-facing Swift concurrency bridge for Flow streams and integrates with Swift `AsyncSequence`.

## Risks
The suspension path uses raw pointers to a local callback variable and to a continuation wrapper, so correctness depends on the generated C++ callback retaining or copying what it needs before stack values disappear. `withCheckedThrowingContinuation` will diagnose double-resume or never-resume issues only in checked runtime modes. Error translation only special-cases `end_of_stream`; all other Flow errors become `GeneralFlowError`. Mutating access to `waitNext` means concurrent iteration over the same stream value could race or consume out of order if wrappers allow sharing.

## Test Signals
Swift tests should cover immediate ready values, immediate end-of-stream, immediate error, delayed callback delivery, async-for iteration, cancellation behavior if supported by the C++ stream, and double/no-resume diagnostics. Interop tests should validate pointer lifetime assumptions across the generated `SingleCB.set` implementation.
