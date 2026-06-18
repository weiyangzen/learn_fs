<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/local_lock.rs -->
# sources/object-store/rustfs/crates/lock/src/local_lock.rs

Purpose: `local_lock.rs` adapts high-level `LockRequest`/`LockType` APIs to the fast local `GlobalLockManager`, returning `FastLockGuard` instances for namespace-local locking.

Important APIs/types/functions: `LocalLock` stores a `namespace: String` and `Arc<GlobalLockManager>`. Public methods expose construction, namespace access, resource-key formatting, and convenience `lock_guard`/`rlock_guard` methods. The central internal method is `acquire_guard`, which converts `LockRequest` into `ObjectLockRequest`.

Control flow: `acquire_guard` clones the request resource, maps `LockType::{Exclusive,Shared}` to `LockMode::{Exclusive,Shared}`, converts owner to `Arc<str>`, maps `types::LockPriority` to `fast_lock::types::LockPriority`, preserves acquire timeout and TTL as lock timeout, then awaits `GlobalLockManager::acquire_lock`. Any fast-lock error is collapsed to `Ok(None)`. Convenience methods construct `LockRequest` values with requested timeout and TTL before calling `acquire_guard`.

State and persistence behavior: `LocalLock` itself stores only namespace and manager reference. It does not maintain a local table; all lock state lives in the global manager/shards. Resource-key formatting is just a string helper and is not used to namespace the `ObjectKey` passed to the manager.

Dependencies and integration points: used by `NamespaceLock::Local` in `namespace/mod.rs`. It bridges crate-level types from `types.rs` and fast-lock types from `fast_lock/types.rs`. `LocalClient` in the client module performs a related adaptation for distributed-lock clients.

Risks: errors are swallowed into `Ok(None)`, so callers lose the distinction between timeout, conflict, disabled behavior, and internal fast-lock errors. The namespace string is not incorporated into the actual `ObjectKey`; two `LocalLock` instances sharing the same manager but different namespaces can conflict if they use the same bucket/object/version. If namespace isolation is expected, callers must encode namespace into the object key or this module must change. Priority mapping must stay in sync between the two enum definitions.

Test signals: namespace tests cover local-manager construction, local write/read guard acquisition, guard release, health and stats defaults, and wrapper behavior. Tests do not currently cover namespace collision between two local namespaces on the same manager.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/local_lock.rs -->
