# sources/storage-engines/wiredtiger/test/model/src/core/kv_table_item.cpp

Purpose: implements per-key update chains with MVCC visibility, transaction conflict checks, prepare conflicts, timestamp fixing, and rollback.

Important APIs and functions: `add_update_nolock` validates non-timestamped/timestamped mixing, detects transaction conflicts against snapshots and uncommitted updates, enforces insert/update existence constraints, and inserts updates sorted by commit timestamp. `get` implements read-own-writes, non-transactional reads, transactional snapshot visibility, prepare conflicts, and stable/durable timestamp filtering. `contains_any` checks all visible updates at a timestamp. `fix_timestamps` removes placeholder timestamp updates, sets final commit/durable timestamps, and reinserts. `rollback_to_stable` removes prepared, out-of-snapshot, or too-new durable updates.

Control flow and state: `_updates` is a sorted deque of shared `kv_update` pointers guarded by `_lock`. Failed conflicts mark the owning transaction failed and throw `WT_ROLLBACK`. Rollback paths remove transaction references to break ownership cycles.

Dependencies and integration: used by `kv_table`; depends on `kv_update`, `kv_transaction`, checkpoints, and WiredTiger error constants.

Risks and test signals: visibility rules are the model's most sensitive behavior. Prepared reads use prepare timestamp ordering, while other operations mostly use commit timestamp ordering. Incorrect reinsertion or durable timestamp filtering would cause verifier mismatches after prepare/commit/RTS/checkpoint workloads.
