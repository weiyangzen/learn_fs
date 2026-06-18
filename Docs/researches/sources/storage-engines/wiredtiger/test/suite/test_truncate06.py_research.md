<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate06.py

Purpose: Tests timestamped truncate over timestamped updates/removes in the presence of older history, with fast-delete, checkpoint, and conflicting/non-conflicting timestamp cases.

Important APIs/types/functions: `test_truncate06` uses scenario dimensions for update vs remove, eviction, checkpoint, and truncate timestamp. Helpers include `evict` with `debug=(release_evict)` and `truncate`, which can use either `session.truncate` or per-key `remove` reference mode.

Control flow: The test writes 10,000 rows at timestamp 10, marks them stable, modifies every other even key in the middle third at timestamp 20, optionally evicts and checkpoints, then truncates a broad range at timestamp 15 or 25 using a read timestamp one less than commit. Timestamp 15 should conflict and return `WT_ROLLBACK`; timestamp 25 should commit.

State and persistence behavior: It covers history chains with stable baseline data and newer updates/removes, with pages optionally in fast-delete-eligible disk state.

Dependencies and integration points: Integrates timestamp conflict detection, fast-delete, checkpointing, update versus tombstone history, row/column formats, and rollback error handling.

Risks: The same logical operation can run through fast-delete or instantiated pages, and bugs may only occur in one path. The disabled remove reference scenario is useful for debugging but not normally part of coverage.

Test signals: Exact `WT_ROLLBACK` versus success depending on truncate time, followed by stable timestamp advancement for clean shutdown.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate06.py -->
