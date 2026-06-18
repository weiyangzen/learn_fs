## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/PerfLevelTest.java

### Purpose

`PerfLevelTest` verifies valid and invalid `PerfLevel` enum handling through Java `RocksDB` APIs.

### Important APIs, Types, And Functions

It uses `RocksDB.setPerfLevel`, `RocksDB.getPerfLevel`, and `PerfLevel` enum constants including `UNINITIALIZED`, `OUT_OF_BOUNDS`, `DISABLE`, `ENABLE_COUNT`, `ENABLE_TIME_EXCEPT_FOR_MUTEX`, `ENABLE_TIME_AND_CPU_TIME_EXCEPT_FOR_MUTEX`, and `ENABLE_TIME`.

### Control Flow

The fixture opens a DB with two CF descriptors. One test asserts invalid sentinel levels throw `IllegalArgumentException`. The other iterates all valid levels, sets each one, and asserts the getter returns the same enum, then resets to `DISABLE`.

### State And Persistence Behavior

Perf level is runtime diagnostic state on the DB/thread context, not persisted database data.

### Dependencies And Integration Points

The test integrates enum ordinal/native value mapping, Java exception validation, and DB-level perf controls.

### Risks And Edge Cases

- Enum additions require updating valid-level coverage.
- Invalid sentinel constants must remain blocked at the Java boundary to avoid undefined native behavior.

### Test Signals

Signals are expected `IllegalArgumentException` for sentinels and exact round-trip for each valid perf level. Static research only; no test command was run.
