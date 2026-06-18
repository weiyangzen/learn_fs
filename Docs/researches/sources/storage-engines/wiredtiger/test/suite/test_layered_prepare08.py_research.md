# sources/storage-engines/wiredtiger/test/suite/test_layered_prepare08.py

## Purpose

This narrow regression test protects a layered cursor comparison guard after the ingest cursor becomes exhausted. It ensures a scan does not assert when a prepared ingest key conflicts, is rolled back, and then disappears before the next scan step.

## Important APIs, Types, and Functions

The class uses leader and follower configs with `cache_size=10MB,statistics=(all),precise_checkpoint=true,preserve_prepared=true`. It opens a follower with `disagg_advance_checkpoint`, creates a prepared transaction on the follower ingest tree, and uses `assertRaisesException` for the expected `WiredTigerError`.

## Control Flow

The leader writes stable keys 1, 3, and 5 and checkpoints. The follower picks up the stable checkpoint and prepares a single ingest key 2 at prepare timestamp 15. A reader at timestamp 20 calls `next()`: stable advances to key 1 while ingest hits key 2 and returns a prepare conflict. The prepared transaction rolls back at timestamp 30, removing key 2. A second `next()` must skip invalid ingest comparison state, return stable key 1, then continue with 3 and 5 before `WT_NOTFOUND`.

## State, Persistence, and Dependencies

State is split between stable checkpoint data and a transient prepared follower-ingest key. The test depends on `wiredtiger`, `wttest`, `helper_disagg`, and `wtscenario`, and integrates with timestamped reads, prepare rollback, and layered cursor current-cursor selection.

## Risks and Test Signals

The risk is an internal assertion or invalid key comparison when the ingest cursor has a ref but no valid current key after rollback. The signal is that the retry returns only the stable keys in order and reaches `WT_NOTFOUND`, proving the merge path handles an unpositioned exhausted ingest cursor.
