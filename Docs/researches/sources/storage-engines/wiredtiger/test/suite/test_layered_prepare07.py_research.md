# sources/storage-engines/wiredtiger/test/suite/test_layered_prepare07.py

## Purpose

This suite verifies that follower cursor operations do not raise `WT_PREPARE_CONFLICT` when the primary has checkpointed unresolved prepared updates and the follower has rolled back its own replayed copy. The follower should return committed values from stable storage.

## Important APIs, Types, and Functions

Key helpers are `setup_primary_and_follower`, `prepare_on_conn`, `checkpoint_with_prepare`, `setup_with_prepare`, `evict_page`, `collect_keys`, `resolve_prepared`, and `run_walk_test`. The connection config enables `statistics=(all),precise_checkpoint=true,preserve_prepared=true`. The suite tests `next`, `prev`, `search`, and `search_near`.

## Control Flow

The common setup commits initial values on both primary and follower, checkpoints them, prepares the same update or delete on both sides using the same prepared ID, and checkpoints the primary with the prepare active. The follower advances to that checkpoint, rolls back its local prepared transaction, evicts affected pages to force reading checkpointed prepared cells, and then scans or searches. Cleanup rolls back the primary prepare, advances stable, and checkpoints so teardown does not see dangling prepared state.

## State, Persistence, and Dependencies

The test deliberately persists prepared cells in the primary checkpoint while also keeping the follower's in-memory transaction state consistent with rollback. It depends on `wiredtiger`, `wttest`, `helper_disagg`, `wtscenario`, and disaggregated checkpoint transfer.

## Risks and Test Signals

The main risk is treating checkpointed prepared cells as active conflicts on a follower after oplog replay rollback has resolved the prepare locally. Signals are sorted key equality for forward and backward scans over prepared updates and tombstones, plus direct `search`/`search_near` assertions that key 2 returns `committed_2` without conflict.
