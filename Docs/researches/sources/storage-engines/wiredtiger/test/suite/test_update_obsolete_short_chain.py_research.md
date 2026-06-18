# sources/storage-engines/wiredtiger/test/suite/test_update_obsolete_short_chain.py

## Purpose
`test_update_obsolete_short_chain.py` verifies that obsolete update pruning does not occur too early for a short update chain, but does occur after a checkpoint once enough obsolete history exists.

## Important APIs, Types, and Functions
The class defines `get_stat`, `update_with_ts`, `pin_timestamps`, and `test_short_chain_no_prune_then_prune`. It uses `SimpleDataSet`, timestamped commits, `conn.set_timestamp`, `stat.conn.cache_obsolete_updates_removed`, and checkpoint.

## Control Flow
The test creates a no-logging table, writes value A at timestamp 10 and pins timestamps, records removed-obsolete stats, writes value B at 20 and verifies the stat did not increase, writes value C at 30, checkpoints, verifies obsolete-removal stat increased, and reads the latest value.

## State and Persistence Behavior
The table keeps timestamped update chains for one key. Checkpoint and timestamp pinning govern when obsolete updates can be pruned.

## Dependencies and Integration Points
Depends on WiredTiger history/update-chain pruning, cache statistics, and timestamp APIs.

## Risks and Edge Cases
The important edge is a short chain where aggressive pruning after the second update would be incorrect.

## Test Signals
Obsolete removed count is unchanged after the second update, increases after checkpoint following the third update, and the latest value is `value-c`.
