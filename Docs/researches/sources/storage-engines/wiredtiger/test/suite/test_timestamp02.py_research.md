# sources/storage-engines/wiredtiger/test/suite/test_timestamp02.py

## Purpose
`test_timestamp02.py` tests core timestamp visibility, oldest/stable/durable timestamp movement, timestamp statistics, and read-your-writes behavior for row and column stores.

## Important APIs, Types, and Functions
The class defines `get_stat`, `check(session, txn_config, expected)`, `test_basic`, and `test_read_your_writes`. Scenarios vary key format. It uses `conn.query_timestamp`, `conn.set_timestamp`, `session.begin_transaction`, `commit_transaction`, `timestamp_transaction`, and connection timestamp statistics.

## Control Flow
`test_basic` inserts keys 1..100 at timestamps matching keys, verifies historical reads, advances oldest, updates keys at timestamps 101..200, manipulates durable timestamp, sets stable, verifies mixed old/new reads, advances oldest, deletes keys at timestamps 201..300, and verifies deletion visibility. It then validates invalid oldest/stable movements, combined timestamp setting, forced oldest movement, and related statistics. `test_read_your_writes` starts a read-timestamp transaction, assigns a later commit timestamp, writes, and verifies the transaction sees its own write.

## State and Persistence Behavior
The table stores timestamped versions and tombstones. Connection timestamp state controls what reads are legal and what versions are visible. Statistics track oldest/stable/durable/force timestamp calls.

## Dependencies and Integration Points
It integrates with WiredTiger MVCC timestamp visibility, timestamp query APIs, cursor iteration/search, stats cursors, and scenario generation.

## Risks and Test Signals
Risks include incorrect timestamp ordering validation, visibility errors across updates/deletes, and stats regressions. Signals are exact dictionaries at many read timestamps and exact error messages/stat counters.
