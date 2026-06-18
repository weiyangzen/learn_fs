# sources/storage-engines/wiredtiger/test/suite/test_timestamp09.py

## Purpose
`test_timestamp09.py` is the string-configuration counterpart to timestamp API validation, covering commit/read timestamp ordering and oldest/stable constraints.

## Important APIs, Types, and Functions
The class uses `session.timestamp_transaction`, `session.commit_transaction`, `begin_transaction(read_timestamp=...)`, `conn.set_timestamp`, `conn.query_timestamp`, and standalone versus MongoDB-build error handling.

## Control Flow
The test creates a table, writes initial data, verifies that a second commit timestamp in one transaction cannot move earlier than the first, verifies `commit_transaction` also rejects earlier timestamps, checks commit timestamps older than oldest via both APIs, validates oldest/stable ordering and monotonic movement, verifies commit timestamps must be after stable, commits records with timestamps 6, 8, and 7, rejects reads below oldest, checks visibility of key 8 at read timestamps 7 and 8, queries `oldest_reader`, forces oldest backwards, and verifies a read below the forced oldest is still rejected while timestamp 6 updates `oldest_reader`.

## State and Persistence Behavior
The test maintains several timestamped versions in one table and exercises connection timestamp state. No restart or checkpoint is needed.

## Dependencies and Integration Points
It integrates with string timestamp config parsing, transaction visibility, timestamp query APIs, and build-specific diagnostics.

## Risks and Test Signals
Risks include inconsistent error ordering or stale oldest-reader calculation. Signals are exact errors, point-read results, and timestamp query equality.
