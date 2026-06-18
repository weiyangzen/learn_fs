<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/src/locking.rs -->
# sources/storage-engines/tikv/components/external_storage/src/locking.rs

Purpose: this module implements advisory remote locks over eventually regular `ExternalStorage` operations, assuming strong consistency for PUT and LIST. It supports shared read locks and exclusive write locks through an intent-file, write-and-verify protocol.

Important APIs and types: `LockMeta` serializes lock metadata: timestamp, host, pid, transaction id, and hint. `RemoteLock` records a lock file path and txn id and exposes `unlock`. `LockExt` adds async `lock_for_read` and `lock_for_write`. `ExclusiveWriteCtx` exposes `txn_id`, `intent_file_name`, `verify_only_my_intent`, and prefix checks. `ExclusiveWriteTxn` describes a transactional write with a target path, content, and optional verify step. `ExclusiveWriteExt` implements `exclusive_write` for `dyn ExternalStorage`.

Control flow: `exclusive_write` generates a UUID, verifies only the current intent can exist, runs transaction-specific verification, writes an empty intent file, re-verifies, writes the final lock file content, then deletes the intent. Read locks write `$path.READ.<random>` and verify no `$path.WRIT` file exists. Write locks write `$path.WRIT` and verify no files under the base lock prefix except the current intent exist. `unlock` reads the lock file, deserializes `LockMeta`, checks the txn id, and deletes the file.

State and persistence behavior: lock state is encoded entirely as remote objects. Intent files are temporary but may remain if a process dies before cleanup. There is no TTL, lease renewal, or automatic stale-lock cleanup.

Dependencies and integration points: it uses `serde_json`, `uuid`, `chrono`, TiKV hostname/pid helpers, `iter_prefix`, `write`, `read`, and `delete` from `ExternalStorage`. It is useful for backup/restore coordination over object stores with strong listing semantics.

Risks: the module documents possible live locks under heavy contention and performs no internal retries. Correctness depends on strong consistency for both PUT and LIST; weaker stores can admit multiple writers. Stale intent or lock files can block future lockers indefinitely. `unlock` refuses to delete if metadata txn id does not match, which protects against deleting someone else's lock.

Test signals: tests use `LocalStorage` to verify read locks block writes, write locks block reads, unlocking permits later locks, and mismatched txn ids cannot unlock others' locks.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/external_storage/src/locking.rs -->
