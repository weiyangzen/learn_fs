# sources/storage-engines/rocksdb/util/slice_transform_test.cc

## Purpose

Tests built-in prefix transforms, especially capped-prefix behavior and integration with prefix bloom filters in a real DB.

## APIs, control flow, and state

`CapPrefixTransform` constructs capped transforms of lengths 6, 8, 10, and 0, checking `Transform` and `SameResultWhenAppended`. `SliceTransformDBTest` opens a temporary DB with `NewCappedPrefixTransform(8)`, block-based bloom filter policy, and whole-key filtering disabled. It writes several keys, flushes them, seeks through an iterator, and checks bloom filter ticker counters for matches and filtered seeks.

## Dependencies and integration

The test depends on `rocksdb/db.h`, `Env`, table/filter/statistics APIs, and the test harness. It validates not just transform output but how prefix extraction drives non-last-level filter checks.

## Risks and test signals

Signals include exact capped prefixes for short and long keys, zero-length cap behavior, iterator validity, returned values, and `NON_LAST_LEVEL_SEEK_FILTER_MATCH`/`FILTERED` ticker counts. The main risk area is a mismatch between transform domain semantics and table filter lookup behavior.
