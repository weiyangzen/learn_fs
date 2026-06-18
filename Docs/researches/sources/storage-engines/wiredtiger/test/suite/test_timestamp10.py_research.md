# sources/storage-engines/wiredtiger/test/suite/test_timestamp10.py

## Purpose
`test_timestamp10.py` verifies saving/querying last checkpoint and recovery timestamps across close, recovery, and optional `wt` utility runs.

## Important APIs, Types, and Functions
The class uses `suite_subprocess`, `runWt`, `conn.query_timestamp('get=last_checkpoint')`, `conn.query_timestamp('get=recovery')`, and helpers `data_and_checkpoint` and `close_and_recover`. Scenarios vary key format, close `use_timestamp` mode, and number of `wt list` runs.

## Control Flow
`data_and_checkpoint` creates an oplog-like logged table and three collection-like non-logged tables, inserts separate timestamp ranges into each collection, sets oldest/stable slightly behind each range, checkpoints, and asserts `last_checkpoint` equals the stable timestamp for each checkpoint. `close_and_recover` closes with default, `use_timestamp=true`, or `use_timestamp=false`, optionally runs the `wt` tool one or two times, reopens, and asserts recovery timestamp. The main test verifies logged data is always present and only the last collection loses unstable records when closing with stable timestamp behavior.

## State and Persistence Behavior
Logged oplog data has commit-level durability. Non-logged collections depend on stable checkpoint recovery when `use_timestamp` is true/default. The recovery timestamp should survive intervening `wt` utility opens.

## Dependencies and Integration Points
It integrates close-time timestamp policy, recovery timestamp metadata, checkpoint timestamp metadata, logging, subprocess `wt`, and cursor verification.

## Risks and Test Signals
Risks include wrong default close policy or losing recovery timestamp after utility opens. Signals are exact `last_checkpoint`/`recovery` timestamps and expected recovered data sets.
