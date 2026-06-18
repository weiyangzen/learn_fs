# sources/storage-engines/wiredtiger/test/suite/test_txn25.py

## Purpose
`test_txn25.py` verifies write generation cleanup across restart so old on-disk transaction IDs do not hide the latest data after IDs restart from low values.

## Important APIs, Types, and Functions
The class defines `getkey` and `test_txn25`, with scenarios for row/column keys and logging/no-logging connection configs. It uses a long-running transaction, repeated per-row commits, checkpoint, `reopen_conn`, and read assertions.

## Control Flow
The test creates a file, holds a second session transaction open, writes all rows three times with values A, B, and C in separate transactions, checkpoints to force pages with transaction IDs to disk, rolls back the pinned transaction, reopens, and reads all rows in a new transaction.

## State and Persistence Behavior
The key state is persisted cell transaction IDs/write generations. After restart, transaction IDs begin again, so stale IDs in cells must be wiped or ignored correctly.

## Dependencies and Integration Points
Depends on WiredTiger restart behavior, checkpointing, write generation logic, and scenario-specific key formatting.

## Risks and Edge Cases
Holding transaction IDs around before checkpoint is required to create the on-disk condition. Bugs may show as older values or not-found rows after reopen.

## Test Signals
Every row reads as the final `value3` after reopening.
