<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor19.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor19.py

Purpose: tests version cursor output for `WT_CURSOR.modify` update chains.

Important APIs and control flow: row and variable-column scenarios create a file with string values. The test inserts an initial 100-character value at timestamp 1, applies several single-byte `wiredtiger.Modify` operations at timestamps 5, 10, and 15, evicts to force some versions to disk/history store, applies more modifies at timestamps 20 and 25, deletes at timestamp 30, then opens `debug=(dump_version=(enabled=true))` and verifies each version in descending order.

State, persistence, and dependencies: state includes modify deltas, full materialized values, history-store/on-disk locations, and a final tombstone. Dependencies are `wiredtiger.Modify`, timestamp commits, eviction cursor, and version cursor value-field layout.

Integration points: covers interaction between modify records, reconciliation/history store, and debug version cursor reporting.

Risks and test signals: expected `type` and `location` values are internal and can shift if version cursor schema changes. Pass signal is exact sequence of values and timestamps from newest to oldest ending in `WT_NOTFOUND`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor19.py -->
