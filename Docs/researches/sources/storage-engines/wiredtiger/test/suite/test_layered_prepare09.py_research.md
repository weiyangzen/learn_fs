# sources/storage-engines/wiredtiger/test/suite/test_layered_prepare09.py

## Purpose

This suite tests follower step-up when a leader checkpoint captures unresolved prepared transactions. It verifies that replicated prepare resolution on the follower, either commit or rollback, produces the correct durable history after the follower becomes leader.

## Important APIs, Types, and Functions

The class is skipped for tiered hooks, uses `preserve_prepared=true`, and scenarios vary `commit=True/False`. Helpers `_open_follower`, `_checkpoint`, and `_step_up` apply checkpoint metadata, checkpoint a connection, and promote a follower by reconfiguring `disaggregated=(role="leader")`. Tests use `disagg_get_complete_checkpoint_meta`, prepared IDs, commit/durable timestamps, rollback timestamps, and timestamped reads.

## Control Flow

Each captured-prepare test builds leader history, leaves a prepare unresolved while stable is advanced beyond the prepare timestamp, checkpoints, stores checkpoint metadata, rolls back the leader copy, and closes the leader without another checkpoint. A follower opens on that metadata, replays the same prepared operation, resolves it by scenario, steps up, and verifies reads at historical timestamps. Cases cover prepared inserts, updates followed by newer updates, deletes, a delete between older and newer committed values, and multiple updates to the same key within one prepared transaction. The not-captured tests set `prepare_ts > stable_ts` at checkpoint time and verify the follower sees only durable pre-prepare state without replay.

## State, Persistence, and Dependencies

State is persisted through checkpoint metadata rather than normal checkpoint pickup. The tests depend on `wiredtiger`, `wttest`, `helper_disagg`, and `wtscenario`. They integrate with disaggregated role changes, prepared transaction replication, durable timestamp semantics, and historical timestamp reads.

## Risks and Test Signals

Risks include applying unresolved prepares twice, losing rollback semantics, exposing prepares not durable at checkpoint time, or mishandling multiple writes to one key. Signals are precise timestamp reads: original values before prepare, commit-vs-rollback behavior at resolution timestamps, newer value preservation at timestamp 220, and `WT_NOTFOUND` for committed prepared deletes or absent not-captured inserts.
