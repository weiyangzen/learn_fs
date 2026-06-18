<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor17.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor17.py

Purpose: tests the `cursor.largest_key()` interface under deletes, timestamps, prepared updates, truncation, empty tables, and cursor positioning.

Important APIs and control flow: scenarios cover file/table row and variable-length column stores plus a complex table case. Helpers populate datasets. Tests delete the largest key and observe globally deleted behavior before/after eviction, insert uncommitted/aborted/timestamp-invisible/prepared larger keys and check `largest_key`, verify `largest_key` sets key but not value, check empty-table `WT_NOTFOUND`, and test fast/slow truncate interactions with timestamps.

State, persistence, and dependencies: state includes update chains, tombstones, evicted pages, timestamps, prepared transactions, and truncate records. Dependencies are datasets, `wiredtiger`, `timestamp_str`, `debug=(release_evict)`, and transaction APIs.

Integration points: covers largest-key calculation across memory, disk, visibility rules, and access methods.

Risks and test signals: several expectations intentionally expose physical largest keys even when logically invisible, so semantics are subtle. Hook skips prevent timestamp interference. Pass signals are exact returned keys and `WT_NOTFOUND` for empty data.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor17.py -->
