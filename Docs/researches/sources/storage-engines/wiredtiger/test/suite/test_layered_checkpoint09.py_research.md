# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint09.py

Purpose: verifies checkpoint-size and database-size accounting for disaggregated metadata under simple, large, repeated, no-checkpoint, follower-no-pickup, deferred-checkpoint, and multi-table cases.

Important APIs/types/functions: class uses `verifyUntilSuccess`, `reopen_conn(config=...,verify_metadata=true)`, `open_conn`, `close_conn`, role reconfiguration, `session.checkpoint`, cursor updates/removes, and `disagg_get_complete_checkpoint_meta` indirectly through verify startup behavior.

Control flow: the first four tests create layered data sets of increasing complexity, checkpoint, and call verify. Database-size tests reopen with `verify_metadata=true` after checkpointed writes; deliberately avoid shutdown checkpoints by stepping down to follower; reopen without checkpoints; recreate/checkpoint after deferred no-checkpoint startup; open as follower without checkpoint metadata; and run a multi-table sequence with size growth and negative deltas from deletes.

State and persistence behavior: the core persistent field is shared metadata `database_size` relative to btree checkpoint sizes plus fixed overhead. Some paths intentionally leave database size and checkpoint sizes at zero to ensure verification skips comparison until there is a meaningful checkpoint/pickup.

Dependencies/integration points: disaggregated metadata verification path, checkpoint size accounting, startup verify, follower open behavior, and metadata update logic across table changes.

Risks: large data counts make runtime heavier. Tests rely on verify skipping in zero/no-pickup cases rather than directly asserting internal counters, so log/debug regressions could be missed unless they become verify failures.

Test signals: pass means metadata database-size accounting matches checkpoint sizes when applicable and avoids false mismatch checks when no checkpoint or pickup has populated the accounting state.
