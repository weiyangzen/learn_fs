# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/NativeFuture.java

## Purpose
`NativeFuture` is the common bridge from FoundationDB native futures to Java `CompletableFuture`s, handling callback registration, result marshaling, cancellation, close, and native pointer synchronization.

## Important APIs, Types, And Functions
Subclasses implement `getIfDone_internal`. `registerMarshalCallback` installs a JNI callback that schedules `marshalWhenDone` on an executor. `close` disposes the native future and fails incomplete Java futures. `cancel` cancels both Java and native futures. `getPtr` asserts read-lock ownership and rejects closed futures.

## Control Flow
Subclasses construct with a native pointer, initialize their fields, then call `registerMarshalCallback`. Native readiness invokes the Java callback at most once; `marshalWhenDone` locks, extracts the typed value, completes or completes exceptionally, and calls `postMarshal`. Most subclasses inherit `postMarshal` close behavior; range chunk subclasses override it.

## State And Persistence Behavior
The class stores a mutable native pointer protected by a read/write lock. Closing atomically zeros the pointer and disposes native resources. Completion state is inherited from `CompletableFuture`.

## Dependencies And Integration Points
All typed future classes extend it. It depends on JNI functions for callback registration, disposal, cancellation, error retrieval, and readiness.

## Risks And Edge Cases
Registering callbacks in the base constructor would race subclass initialization, hence the explicit pattern. Range future subclasses that override `postMarshal` must be closed manually after result extraction. Closing an incomplete future changes Java completion to `IllegalStateException`.

## Test Signals
Tests should cover callback completion, subclass initialization order, native exception propagation, close/cancel races, range-future manual close behavior, and `getPtr` after close.
