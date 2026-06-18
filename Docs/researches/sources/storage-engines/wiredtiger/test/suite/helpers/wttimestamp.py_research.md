<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/wttimestamp.py -->
# sources/storage-engines/wiredtiger/test/suite/helpers/wttimestamp.py

Purpose: Lightweight timestamping layer used by the timestamp hook and dataset helpers to transparently timestamp cursor mutations.

Important APIs and types: `WiredTigerTimeStamp` stores a monotonically increasing integer with `incr`, `get_incr`, and `get`. `session_timestamped_transaction` is a context manager that begins/commits or timestamps an existing transaction. `TimestampedCursor` proxies a `wiredtiger.Cursor` and overrides `insert`, `update`, `remove`, and `modify`.

Control flow: When a timestamp generator exists and the session is not already in a transaction, the context manager begins a transaction, yields to the operation, then commits with `commit_timestamp=<next>`. If a transaction is already active, it yields and then calls `timestamp_transaction` with the next timestamp. `TimestampedCursor` delegates all other methods to the wrapped cursor via `__getattr__`.

State and persistence behavior: Timestamp state is in-memory per `WiredTigerTimeStamp`. Persistent behavior is in commit timestamps applied to WiredTiger updates. The cursor wrapper initializes `session._has_transaction` if missing, while the timestamp hook keeps that flag accurate by replacing transaction APIs.

Dependencies and integration points: Used by `wtdataset.BaseDataSet.open_cursor` and `truncate`, and supplied through `hook_timestamp.TimestampPlatformAPI`. Depends on WiredTiger session transaction/timestamp APIs and testcase timestamp formatting expectations.

Risks: Correct behavior depends on `_has_transaction` being maintained by hooks; without it, nested transaction detection can be wrong. The timestamp counter is simple and not synchronized for multi-threaded mutation. Exceptions inside the yielded operation do not explicitly roll back.

Test signals: Timestamped dataset tests should see commits at increasing timestamps, stable reads at selected timestamps, and no nested transaction errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/wttimestamp.py -->
