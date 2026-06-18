# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionOptionsFIFOTest.java

## Purpose

Accessor coverage for FIFO compaction-specific options.

## Important APIs, control flow, and dependencies

The tests create `CompactionOptionsFIFO`, set `maxTableFilesSize` and `allowCompaction`, and assert getter values.

## State, persistence, risks, and test signals

Only native option state is allocated. Risks are unsigned size conversion and default/native field drift. Signals are exact getter equality after setter calls.
