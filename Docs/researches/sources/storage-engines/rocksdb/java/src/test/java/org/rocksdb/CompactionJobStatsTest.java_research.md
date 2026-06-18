# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionJobStatsTest.java

## Purpose

Verifies default and reset behavior for the Java `CompactionJobStats` wrapper.

## Important APIs, control flow, and dependencies

The file constructs `CompactionJobStats`, calls `reset` and `add`, and reads all exposed counters: elapsed time, input/output record and file counts, manual-compaction flag, byte totals, replaced/deletion/corrupt counts, file IO timing counters, output key prefixes, and single-delete stats.

## State, persistence, risks, and test signals

No DB state is involved. The important state is the native stats object and Java conversion of integral counters and byte-prefix arrays. Risks include newly added native fields not being exposed consistently, nonzero uninitialized memory, and incorrect reset/add JNI binding. Signals are zero/false/empty defaults and no exception from adding another stats object.
