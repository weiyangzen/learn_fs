<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/testing/Promise.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/testing/Promise.java

## Purpose
`Promise` is a JNI-backed one-shot boolean completion object used by Java workloads to signal native test harness phases.

## Important APIs, Types, And Functions
It stores a native pointer `nativePromise`, a `wasSet` flag, private constructor, `canBeSet`, and `send(boolean)`, which calls a native static `send(long, boolean)`.

## Control Flow, State, And Persistence
`send` rejects second completion with `IllegalStateException`, sets `wasSet`, and forwards the value to native code. State is local plus the native promise handle.

## Dependencies And Integration Points
It integrates with `AbstractWorkload.setup/start/check` and native simulation code that can construct instances despite the private constructor.

## Risks And Test Signals
`wasSet` is not synchronized, so concurrent send attempts can race. Native pointer lifetime is external. Tests should cover one-shot behavior, double-send failure, and JNI completion observed by the harness.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/testing/Promise.java -->
