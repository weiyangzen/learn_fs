# sources/storage-engines/wiredtiger/test/model/src/include/model/kv_transaction.h

Purpose: declares model transactions, including state transitions, timestamps, snapshots, update ownership, rollback/commit behavior, and optional WT debug-log metadata.

Important APIs and types: `kv_transaction_state` (`in_progress`, `prepared`, `committed`, `rolled_back`), `k_initial_commit_timestamp`, constructor, accessors for ID/timestamps/state/snapshot/failure, `visible_update`, `add_update`, `commit`, `prepare`, `fail`, `reset_snapshot`, `rollback`, `set_commit_timestamp`, `set_wt_metadata`, `wt_id`, and `wt_base_write_gen`.

Control flow: a transaction starts in progress with a database snapshot and a temporary max commit timestamp. Writes are incorporated into table item chains first, then registered through `add_update`. Prepare records a prepare timestamp and changes state. Commit fixes timestamps on registered updates, removes itself from the database active set, and marks committed. Rollback asks tables to roll back each update and marks rolled back. Reset snapshot obtains a new database snapshot.

State and persistence: the transaction stores commit/durable/prepare/read timestamps, snapshot pointer, database reference, update lists, nontimestamped update list, failed flag, atomic state, and WT transaction metadata. It must not outlive its database. Update lists create shared-pointer cycles with updates until commit/rollback cleanup.

Dependencies and integration: includes `core.h`, `data_value.h`, `kv_transaction_snapshot.h`, and `kv_transaction_update.h`; interacts with `kv_database`, `kv_table`, and `kv_update`. Runners and WT test macros drive lifecycle methods.

Risks: state transitions must be serialized by `_lock` and atomic state. `set_wt_metadata` is only valid before updates are added. A failed transaction should be rolled back by guards. The initial commit timestamp of max makes pre-commit updates sort late and must be repaired before visibility becomes final.

Test signals: transaction tests should cover commit with/without timestamps, durable timestamp, prepare/commit/rollback, reset snapshot visibility, failed guard rollback, WT metadata import, and invalid state transitions.
