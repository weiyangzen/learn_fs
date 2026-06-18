# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/NativeObjectWrapper.java

## Purpose
`NativeObjectWrapper` is the base class for closeable Java objects that own a native FoundationDB pointer, such as databases and transactions.

## Important APIs, Types, And Functions
It stores `cPtr`, `closed`, and a read/write lock. `close` atomically marks the wrapper closed and invokes subclass `closeInternal(ptr)`. `getPtr` asserts read-lock ownership and rejects closed access. `checkUnclosed` prints leak warnings based on `FDB.instance().warnOnUnclosed`.

## Control Flow
Subclasses lock `pointerReadLock`, call `getPtr`, and invoke JNI. When closed, the write lock prevents new pointer readers, zeros the pointer, and delegates native disposal outside the lock.

## State And Persistence Behavior
Pointer state is in-memory and terminal after close. No persistent state exists. Finalizers in subclasses call `checkUnclosed` and `close`.

## Dependencies And Integration Points
`FDBDatabase`, `FDBTransaction`, and deprecated `Cluster` extend it.

## Risks And Edge Cases
The read-lock assertion is not enforcement when assertions are disabled, so callers must follow the locking convention. Finalizer-based cleanup is nondeterministic. `Cluster` passes pointer `0`, making it immediately closed.

## Test Signals
Tests should cover close idempotence, pointer rejection after close, concurrent close versus JNI access, leak warning toggles, and subclass disposal invocation exactly once.
