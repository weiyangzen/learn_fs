# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactRangeOptionsTest.java

## Purpose

Validates Java accessors for manual compaction options and cancellation state.

## Important APIs, control flow, and dependencies

The test uses `CompactRangeOptions`, `BottommostLevelCompaction`, and `Slice`. It round-trips `exclusiveManualCompaction`, `bottommostLevelCompaction`, `changeLevel`, `targetLevel`, `targetPathId`, `allowWriteStall`, `maxSubcompactions`, `fullHistoryTSLow`, and `canceled`. Cancellation is toggled by repeated `setCanceled` calls.

## State, persistence, risks, and test signals

No DB state is created. The important state is native option storage, including nullable timestamp slices and the sticky cancellation flag. Risks are enum drift, null slice handling, and incorrect boolean defaults. Signals are default assertions, round-trip equality, and cancellation behavior.
