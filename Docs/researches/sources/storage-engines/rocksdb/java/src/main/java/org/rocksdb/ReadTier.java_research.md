# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ReadTier.java

## Purpose
`ReadTier` is the Java enum mirror for RocksDB read-tier configuration. It lets `ReadOptions` restrict reads to all storage, block cache, persisted data, or memtable-resident data depending on the caller's latency and I/O policy.

## Important APIs, Types, And Functions
- Enum constants: `READ_ALL_TIER`, `BLOCK_CACHE_TIER`, `PERSISTED_TIER`, and `MEMTABLE_TIER`.
- `getValue()` exposes the native byte code.
- `getReadTier(byte)` maps native bytes back to Java and throws for invalid values.

## Control Flow
`ReadOptions.setReadTier` writes `readTier.getValue()` into the native `ReadOptions`. `ReadOptions.readTier()` reads the native byte and resolves it through `getReadTier(byte)`.

## State And Persistence Behavior
The enum is immutable and stateless beyond byte metadata. Selected read tier is per-`ReadOptions` runtime state, not persisted in the database.

## Dependencies And Integration Points
- Directly integrated with `ReadOptions`.
- Native JNI casts the byte to `rocksdb::ReadTier` and back from the native `read_tier` field.
- Read APIs may throw `RocksDBException` when the chosen tier cannot satisfy a read, for example cache-only reads that miss required data.

## Risks And Edge Cases
- Byte values must match the native `ReadTier` enum.
- Null passed to `ReadOptions.setReadTier` produces a Java `NullPointerException`.
- The Javadoc says `getReadTier` may return null, but the implementation throws on invalid values.

## Test Signals
- `ReadOptionsTest` covers setting `BLOCK_CACHE_TIER` and retrieving it.
- Broader behavior is exercised by read-path tests using `ReadOptions`, but cache/persisted/memtable miss semantics need integration tests with controlled storage/cache state.
