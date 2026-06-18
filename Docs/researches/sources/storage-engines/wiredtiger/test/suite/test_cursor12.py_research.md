<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor12.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor12.py

Purpose: comprehensive smoke and recovery test for the `WT_CURSOR.modify` API over string and byte-array values.

Important APIs and control flow: scenario matrix covers file/table, record-number/string keys, and `S`/`u` values. A large modification table describes no-ops, replacement, growth, shrink, discard, gaps, overlap, and many modifications. Helpers convert bytes, build `wiredtiger.Modify` records, apply mods inside snapshot transactions, and confirm final values. Tests also reject modify under read-uncommitted/read-committed, verify persistence after reopen and crash-copy recovery, stress 50000 modifications to one value, and verify not-found behavior after delete or aborted/uncommitted insert.

State, persistence, and dependencies: state includes update chains, logged recovery copies, checkpointed pages, and value-format-specific bytes/strings. Dependencies are `copy_wiredtiger_home`, `SimpleDataSet`, random/string, and transaction isolation.

Integration points: covers modify API semantics, reconciliation, recovery, rollback visibility, and Python binding type conversion.

Risks and test signals: byte/string conversion and null padding are easy to regress. Pass signals are exact final values across in-memory, reopened, and recovered states plus correct WT_NOTFOUND/error behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor12.py -->
