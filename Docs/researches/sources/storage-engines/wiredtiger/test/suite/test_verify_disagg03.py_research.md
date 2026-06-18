# sources/storage-engines/wiredtiger/test/suite/test_verify_disagg03.py

## Purpose

`test_verify_disagg03.py` verifies that opening a disaggregated follower with `verify_metadata=true` succeeds when checkpointed data includes later timestamped deletions of earlier writes.

## Important APIs, Types, and Functions

The class uses disaggregated storage scenarios, leader config, layered URI/table config, and `test_verify_metadata_follower_with_deletions`. It calls `disagg_get_complete_checkpoint_meta`, `conn.reconfigure`, `close_conn`, and `open_conn`.

## Control Flow

The test creates a layered table, writes all keys at timestamp 5 and checkpoints, overwrites them at timestamp 10 and checkpoints, deletes every other key at timestamp 15 and checkpoints, captures checkpoint metadata, reconfigures the connection from leader to follower to avoid shutdown checkpoint modification, closes it, and reopens as follower with `verify_metadata=true`.

## State and Persistence Behavior

The important state is checkpointed layered data containing multi-version keys and tombstones. The final follower open must be read-only with supplied checkpoint metadata.

## Dependencies and Integration Points

Depends on disaggregated helper fixtures, timestamped transactions, checkpoint metadata export, follower role configuration, and metadata verification at connection open.

## Risks and Edge Cases

The test covers a specific deletion-after-write pattern. It assumes stepping down before close prevents unwanted shutdown checkpoint changes.

## Test Signals

The primary signal is successful follower reopen with `verify_metadata=true`; any metadata verification error fails the test.
