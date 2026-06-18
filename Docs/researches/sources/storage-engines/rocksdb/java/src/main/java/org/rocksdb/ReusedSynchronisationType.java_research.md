# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ReusedSynchronisationType.java

## Purpose
`ReusedSynchronisationType` is a Java enum describing which synchronization strategy native code should use for reused buffers: a standard mutex, adaptive mutex, or thread-local buffers.

## Important APIs, Types, And Functions
- Enum constants: `MUTEX`, `ADAPTIVE_MUTEX`, and `THREAD_LOCAL`.
- `getValue()` returns the native byte code.
- `getReusedSynchronisationType(byte)` maps byte values back to Java and throws for invalid values.

## Control Flow
The enum itself only maps values. Consuming code passes its byte through JNI into native configuration that chooses the synchronization primitive for reused native buffers.

## State And Persistence Behavior
Only immutable enum byte metadata is stored. The chosen strategy influences native runtime synchronization and memory layout, not persisted RocksDB data.

## Dependencies And Integration Points
- Integrated with native code that configures reused buffer synchronization. The source comments describe native mutex/adaptive mutex/thread-local behavior.
- Must align with the corresponding C++ enum or JNI conversion table used by the buffer-reuse code.

## Risks And Edge Cases
- Wrong byte mapping can change concurrency behavior, potentially causing performance regressions or unsafe sharing if native expectations differ.
- Adaptive mutex can waste CPU under heavy contention; thread-local mode can increase per-thread memory usage.
- No public consumer is visible in this small subset, so changes should be checked against the wider Java/JNI codebase before altering values.

## Test Signals
- No direct tests were identified for this enum in the inspected Java test references.
- Useful tests would round-trip all byte values through the consuming native option and verify invalid bytes throw.
