# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Priority.java

## Purpose
`Priority` is a Java enum for RocksDB environment thread-pool priorities. It lets Java callers select RocksDB background thread pools, primarily low-priority compaction work and high-priority flush work.

## Important APIs, Types, And Functions
- Enum constants: `BOTTOM`, `LOW`, `HIGH`, and `TOTAL`, with byte values `0x0` through `0x3`.
- Package-private `getValue()` returns the byte sent through JNI.
- Package-private static `getPriority(byte)` maps native byte values back to Java and throws for invalid bytes.

## Control Flow
There is no dynamic control flow beyond byte lookup. Consumers pass a `Priority` to Java environment methods; JNI code receives the byte from `getValue()` and forwards it to native RocksDB.

## State And Persistence Behavior
The enum stores only immutable byte codes. It does not own native resources, does not persist data, and has no synchronization requirements.

## Dependencies And Integration Points
- `Env.setBackgroundThreads` and `Env.getBackgroundThreads` use `Priority` to select the native thread pool.
- Tests in `MixedOptionsTest` configure low and high thread counts on `Env` and `RocksMemEnv`, verifying the enum-to-native path.
- The values must align with RocksDB's C++ `Env::Priority` ordering, including `TOTAL` as a sentinel.

## Risks And Edge Cases
- `TOTAL` is a sentinel rather than a normal scheduling priority; exposing it as a Java enum constant can allow accidental use unless callers follow native API expectations.
- `getValue()` and `getPriority()` are package-private, limiting public misuse but still requiring JNI and same-package code to preserve C++ ordering.

## Test Signals
- Existing Java mixed options tests cover `LOW` and `HIGH` thread pools.
- Additional regression coverage would be useful for invalid `getPriority(byte)` values and for ensuring `TOTAL` is not accepted by APIs that expect only runnable pools if native behavior changes.
