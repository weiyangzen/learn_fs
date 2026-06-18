<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/namespace/mod.rs -->
# sources/object-store/rustfs/crates/lock/src/namespace/mod.rs

Purpose: `namespace/mod.rs` provides the public namespace-lock facade, unifying distributed quorum locks and fast local locks behind `NamespaceLock`, `NamespaceLockGuard`, and `NamespaceLockWrapper`.

Important APIs/types/functions: `NamespaceLockGuard` wraps either `DistributedLockGuard` or `FastLockGuard` and exposes `lock_id`, `key`, `release`, and `is_released`. `NamespaceLockWrapper` stores a lock, resource, and owner for repeated convenience acquisition. `NamespaceLock` variants are `Distributed(DistributedLock)` and `Local(LocalLock)`. Constructors include `new`, `with_client`, `with_local_manager`, `with_clients`, and `with_clients_and_quorum`. Acquisition APIs include `acquire_guard`, `lock_guard`, `rlock_guard`, `get_write_lock`, `get_write_lock_quiet`, and `get_read_lock`. Health/stat APIs are `get_health` and `get_stats`.

Control flow: constructors choose distributed mode for client-based locks and local mode for a `GlobalLockManager`. Multi-client distributed locks default write quorum to majority, while explicit quorum is passed through. Acquisition methods dispatch by enum variant and wrap returned guards. The convenience `get_*` methods convert `Ok(None)` into `LockError::timeout`. `get_write_lock_quiet` suppresses expected distributed contention logs. Health checks run client `is_online` calls in parallel for distributed locks and mark local locks healthy with one connected node. Stats aggregate successful/failed acquires from distributed clients; local stats remain default.

State and persistence behavior: namespace lock objects store either a distributed lock with clients/quorum or a local lock with manager. Guards own release responsibility. No persistent state exists here; distributed state lives in clients/backends and local state in fast-lock shards.

Dependencies and integration points: integrates `DistributedLock`, `DistributedLockGuard`, `LockClient`, `LocalLock`, `FastLockGuard`, `LockRequest`, `LockId`, and crate error/types. Downstream storage layers use `NamespaceLockWrapper` for object and bucket operation serialization.

Risks: local namespace isolation has the same caveat as `LocalLock`: the namespace is not necessarily part of the actual lock key. `get_*` methods map `None` to timeout, which can blur disabled or internal failures. `NamespaceLockGuard::lock_id` is unavailable for fast guards, and `key` is unavailable for distributed guards, so callers must handle variant-specific metadata. Local `get_stats` returns zeros even though fast-lock metrics exist elsewhere.

Test signals: `namespace/tests.rs` broadly covers constructors, local guards, wrapper, health/stats, distributed quorum, rollback, retries, offline clients, read/write quorum differences, slow-client early return, and no-runtime drop.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/namespace/mod.rs -->
