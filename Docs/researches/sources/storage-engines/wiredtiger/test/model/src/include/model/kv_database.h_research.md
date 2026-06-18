# sources/storage-engines/wiredtiger/test/model/src/include/model/kv_database.h

Purpose: declares the top-level in-memory model database containing tables, active transactions, checkpoints, configuration, and oldest/stable timestamps.

Important APIs and types: `kv_database_config` with `disaggregated` and `leader`, default constructor and `from_string`; `kv_database` constructor/destructor; table/checkpoint creation and lookup; `set_config`, `config`; timestamp setters/getters; `begin_transaction`, `remove_inactive_transaction`, `txn_snapshot`; `restart`, `crash`, `start`, and `rollback_to_stable`.

Control flow: clients create tables and transactions through the database. Transaction creation captures a snapshot. Transaction commit/rollback eventually calls `remove_inactive_transaction`. Checkpoint creation captures a checkpoint snapshot and timestamp bounds. Restart/crash paths lock tables, transactions, and checkpoints in declared order, roll back or recover state, and call `start_nolock`. RTS walks tables with a stable timestamp and optional snapshot.

State and persistence: persistent model state is `_tables`, `_checkpoints`, `_oldest_timestamp`, and `_stable_timestamp`; live state is `_active_transactions` and `_last_transaction_id`. The destructor calls `clear()` to break circular references between active transactions and updates. Timestamp setters enforce monotonicity and oldest <= stable.

Dependencies and integration: includes `kv_checkpoint.h`, `kv_table.h`, and `kv_transaction.h`. It is used by runners, debug-log parser, verification tests, and WT utility macros.

Risks: locking order is explicitly documented and must be followed to avoid deadlocks. Recursive table/transaction locks are required because restart rolls back active transactions that also touch database state. `set_config` is not locked. Timestamp getters do not lock, so concurrent mutation may be risky despite timestamp setters locking.

Test signals: model tests should exercise table uniqueness, checkpoint uniqueness, transaction cleanup, timestamp monotonic errors (`EINVAL`), clean restart, crash restart, rollback-to-stable, disaggregated config, and memory cleanup with active transactions.
