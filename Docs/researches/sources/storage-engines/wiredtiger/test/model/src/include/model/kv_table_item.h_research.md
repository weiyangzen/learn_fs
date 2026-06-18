# sources/storage-engines/wiredtiger/test/model/src/include/model/kv_table_item.h

Purpose: declares the per-key version chain for a table, including visibility, prepared update detection, rollback, and timestamp repair.

Important APIs and types: `add_update`, `contains_any`, `exists`, `exists_opt`, checkpoint/transaction/latest `get` overloads, `get_latest`, `fix_timestamps`, `has_prepared`, `rollback_to_stable`, and `rollback_updates`. Protected helpers include `add_update_nolock`, `fail_with_rollback`, internal `contains_any`, internal `get`, and `has_prepared_nolock`.

Control flow: table writes append sorted `kv_update` instances through `add_update`. Reads pass transaction snapshot, transaction ID, read timestamp, and optional stable timestamp into internal `get`, which chooses the visible update or returns `NONE`. Checkpoint reads use stable timestamp and compare durable timestamps. RTS removes or rolls back updates newer than the stable timestamp or not visible to the supplied snapshot.

State and persistence: `_updates` is a deque of `shared_ptr<kv_update>` sorted by update ordering. A mutex protects per-key operations. The chain stores tombstones as updates with `NONE` values and may keep committed, prepared, and in-progress updates until rollback/cleanup.

Dependencies and integration: includes `data_value.h`, `kv_checkpoint.h`, and `kv_update.h`. It is embedded in `kv_table::_data` and depends on transaction snapshots from `kv_checkpoint` and `kv_transaction`.

Risks: update ordering and comparator semantics are central; incorrect insertion can break visibility. Prepared updates may cause conflicts at timestamps before commit. `fail_with_rollback` intentionally marks update failure and throws to simulate WT rollback. Durable timestamp handling differs from commit timestamp for checkpoint reads.

Test signals: tests should verify latest and timestamped reads, checkpoint reads, prepared conflict behavior, duplicate/no-overwrite failures, truncate tombstones, transaction rollback cleanup, RTS filtering, and `contains_any` across duplicate timestamp values.
