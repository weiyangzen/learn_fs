# Research: sources/storage-engines/wiredtiger/test/catch2/truncate/test_truncate_write_conflict.cpp

## sources/storage-engines/wiredtiger/test/catch2/truncate/test_truncate_write_conflict.cpp

Purpose: Comprehensive integration tests for layered-table truncate write-conflict detection: `__wt_layered_table_truncate_detect_write_conflict` for single keys and `__wt_layered_table_truncate_detect_non_ingest_write_conflict` for ranges.

Important fixtures/APIs: `write_conflict_fixture` opens a real disaggregated follower/PALite connection, creates a layered table, opens a cursor, exposes the layered table, and creates additional sessions. Helpers format keys, run operations in committed/rolled-back/uncommitted transactions, set read timestamps, and roll back on scope exit.

Control flow: single-key scenarios cover empty list, outside ranges, inside inclusive boundaries, single-key ranges, multiple ranges, committed ranges not conflicting, own uncommitted range not conflicting, overlapping committed/uncommitted ranges, lock release, and committed truncate becoming a conflict for readers whose read timestamp predates the truncate. Non-ingest range scenarios cover empty list, non-overlap, inclusive-boundary overlap, committed and own-uncommitted exemptions, lock release, timestamp-gated committed conflicts, single-key range overlap, multiple ranges, and mixed committed/uncommitted overlaps.

State and persistence: real WT home `WT_TEST.truncate_write_conflict`, table/cursor state, transaction lifecycles, truncate list, timestamps, locks, and dhandle references.

Dependencies/integration: depends on PALite extension, disaggregated follower mode, public transaction API, layered cursor casts, and truncate visibility. Risks are high setup cost, extension availability, timestamp semantics, and rollback cleanup. Test signals are `0` vs `WT_ROLLBACK` return codes and lock release.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/truncate/test_truncate_write_conflict.cpp -->
