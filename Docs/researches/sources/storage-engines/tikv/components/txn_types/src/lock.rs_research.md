# sources/storage-engines/tikv/components/txn_types/src/lock.rs

Purpose: transaction lock model, persistent lock encoding/decoding, shared-lock container, pessimistic-lock compact representation, and lock conflict checks.

Important APIs/types/functions: `LockType`, `Lock`, `SharedLocks`, `PessimisticLock`, `TxnLockRef`, `LockInfoExt`, `LockOrSharedLocks`, `decode_lock_type`, `decode_lock_start_ts`, `parse_lock`, `check_ts_conflict`, and `check_ts_conflict_for_replica_read`.

Control flow: `Lock::to_bytes` writes a legacy prefix followed by ordered tagged fields such as for-update ts, txn size, min commit ts, async commit secondaries, rollback timestamps, last-change metadata, txn source, conflict flag, and generation. Parsing reads known tags and stops at unknown bytes for forward compatibility. Conflict checks ignore non-conflicting lock types, future/min-commit locks, bypassed start timestamps, and selected latest-primary reads, otherwise returning key-lock or write-conflict errors.

State and persistence: lock bytes are persisted in TiKV lock CF. `SharedLocks` persists multiple lock segments under one shared-lock record and lazily parses segment bytes into `Lock` values on access. `PessimisticLock` is an in-memory compact representation convertible to persisted `Lock`.

Dependencies/integration: depends on TiKV codec helpers, `kvproto::kvrpcpb::LockInfo`, transaction keys/mutations, `TimeStamp`, `TsSet`, and logging redaction wrappers.

Risks: lock encoding is compatibility-sensitive; unknown tags require ordered serialization. `SharedLocks::into_lock_info` unwraps segment parsing. Conflict behavior around `TimeStamp::max`, async commit, one-PC, and replica reads is correctness-critical.

Test signals: extensive tests cover lock type conversion, encode/decode round trips, bad input, unknown-byte forward compatibility, SI and RC conflict behavior, redacted debug output, pessimistic conversion/memory sizing, shared-lock operations, shrink-only enforcement, duplicate insert, and update errors.
