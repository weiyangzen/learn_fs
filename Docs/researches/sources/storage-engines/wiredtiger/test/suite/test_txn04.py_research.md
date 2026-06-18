# sources/storage-engines/wiredtiger/test/suite/test_txn04.py

## Purpose
`test_txn04.py` tests transaction visibility and hot backup recovery for simple transactional operations with commit or rollback outcomes.

## Important APIs, Types, and Functions
The class defines `conn_config`, `check`, `check_all`, `hot_backup`, `ops`, and `test_ops`. It uses `suite_subprocess`, `backup:` cursors, filesystem copying, `wiredtiger_open`, and isolation-level checks.

## Control Flow
For each scenario, the test creates a table, applies an operation inside a transaction, checks current and committed visibility before transaction resolution, commits or rolls back, rechecks, then creates a hot backup and opens it to confirm only committed state is present.

## State and Persistence Behavior
The persisted signal comes from a backup directory opened as a separate WiredTiger home. The backup must contain only durable committed changes.

## Dependencies and Integration Points
Depends on WiredTiger backup cursors, transaction isolation, `suite_subprocess`, `os`/`shutil`, and scenario pruning.

## Risks and Edge Cases
Backup taken around active transactions can reveal improper visibility or copied-log ordering. Scenario pruning reduces exhaustive coverage.

## Test Signals
Visibility dictionaries and backup-open reads must equal the expected committed dictionary.
