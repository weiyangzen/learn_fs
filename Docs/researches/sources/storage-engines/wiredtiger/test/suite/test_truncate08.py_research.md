<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate08.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate08.py

Purpose: Regression test for avoiding `WT_PREPARE_CONFLICT` when iterating after a committed prepared fast-truncate transaction.

Important APIs/types/functions: Uses `session.truncate`, `prepare_transaction`, `timestamp_transaction` for commit and durable timestamps, `commit_transaction`, `simple_key`, `simple_value`, and cursor iteration.

Control flow: The test populates an 80,000-row small-page table, reopens to force disk state, starts a transaction, truncates keys 10,000 through 70,000, writes a replacement value on a fast-truncated page, prepares at 10, commits/durably commits at 20, and then scans the whole table.

State and persistence behavior: It creates a prepared transaction that both fast-deletes a range and modifies a key on a deleted page, then commits it. After commit, no prepared state should remain visible to readers.

Dependencies and integration points: Integrates fast-delete, prepared transaction resolution, modify-after-truncate behavior, and cursor traversal over row/column tables.

Risks: A stale prepared state in deleted-page metadata can leak `WT_PREPARE_CONFLICT` to ordinary readers after commit.

Test signals: Full cursor traversal completes without error; any prepare conflict during `cursor.next()` fails the test.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate08.py -->
