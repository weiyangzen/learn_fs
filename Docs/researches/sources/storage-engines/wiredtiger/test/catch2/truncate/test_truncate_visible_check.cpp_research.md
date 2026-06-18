# Research: sources/storage-engines/wiredtiger/test/catch2/truncate/test_truncate_visible_check.cpp

## sources/storage-engines/wiredtiger/test/catch2/truncate/test_truncate_visible_check.cpp

Purpose: Unit tests for `__wt_truncate_delete_visible_check` as a range-membership and output-buffer helper.

Important fixture/APIs: `TruncVisibleCheckFixture` builds a mock session, transaction shared list, `WT_TXN`, heap `WT_LAYERED_TABLE`, `truncateqh`, rwlock, and helper `add_truncate_entry` using globally visible `WT_TXN_NONE` entries with string-literal keys.

Control flow: sections test misses for empty list, keys before/after ranges, single-key neighbors, and gaps between ranges; hits for strict interior, inclusive start/stop boundaries, single-key exact match, multiple non-overlapping ranges, and overlapping ranges. Additional sections prove read lock release after hit/miss/empty, optional output params, deep-copy of matched start/stop keys, correct range selected, and untouched output buffers on miss.

State and persistence: in-memory truncate entries, WT item buffers allocated for output keys, and lock state. Destructor drains entries and frees session/table structures.

Dependencies/integration: narrower than the full visibility fixture; it assumes entries are globally visible and focuses on range comparison, buffer copy, and lock discipline. Risks include raw string-literal key storage and exact inclusive-boundary expectations. Test signals are return code, output buffer contents, and ability to take write lock.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/truncate/test_truncate_visible_check.cpp -->
