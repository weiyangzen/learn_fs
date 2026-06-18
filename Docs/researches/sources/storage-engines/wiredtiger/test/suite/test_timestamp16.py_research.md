<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp16.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp16.py

Purpose: Confirms that a transaction read timestamp is cleared after rollback or commit and cannot leak into later timestamped checkpoints.

Important APIs/types/functions: `test_timestamp16` extends `WiredTigerTestCase` and `suite_subprocess`. The main API calls are `session.begin_transaction('read_timestamp=...')`, `rollback_transaction`, `commit_transaction`, `session.checkpoint('use_timestamp=true')`, `conn.set_timestamp`, and `conn.query_timestamp('get=last_checkpoint')`.

Control flow: The test creates a table, starts and rolls back a read transaction at timestamp 100, checkpoints with timestamps, and expects `last_checkpoint` to stay zero. It then sets stable timestamp 2, repeats a rollback path, and expects checkpoint timestamp 2. Finally it commits a transaction that had read timestamp 150 and verifies the next timestamped checkpoint remains at stable timestamp 2.

State and persistence behavior: The durable state under test is the checkpoint timestamp stored in connection metadata. The important transient state is the session transaction read timestamp; the test ensures it is reset before checkpoint timestamp selection.

Dependencies and integration points: Connects transaction lifecycle cleanup to checkpoint timestamp selection. It depends on the harness timestamp comparison helper and WiredTiger metadata query path.

Risks: A regression would allow stale read timestamp state to make a checkpoint appear newer than the stable timestamp or to report an unexpected last checkpoint timestamp.

Test signals: Exact `last_checkpoint` assertions provide focused signals for rollback and commit cleanup paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp16.py -->
