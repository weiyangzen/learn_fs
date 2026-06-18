# sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/tier_sweeper.rs

Purpose: Converts lifecycle transition metadata into remote-tier delete journal work and performs bounded remote deletes. It protects the remote tier delete path with a concurrency semaphore, an inflight metric, and a signer/header-error circuit breaker.

Important APIs and types: `ObjSweeper` captures bucket/object versioning and transition state, derives lifecycle `ObjectOpts`, decides `should_remove_remote_object`, and enqueues a `Jentry` to `GLOBAL_ExpiryState`. `Jentry` implements `ExpiryOp` with a stable hash over tier and object names. `delete_object_from_remote_tier` obtains the tier driver from `GLOBAL_TierConfigMgr` and calls `remove`. `transitioned_delete_journal_entry` and `transitioned_force_delete_journal_entry` are small public helpers for regular and force-delete paths.

Control flow and state: A remote object is journaled only after `TRANSITION_COMPLETE`. Non-versioned buckets, suspended buckets, and concrete version IDs are eligible; null/current version handling is intentionally more conservative. The sweeper chooses an expiry worker channel by operation hash and records missed tasks if no channel exists or send fails. Remote delete first checks the breaker, acquires `REMOTE_DELETE_LIMITER`, increments `REMOTE_DELETE_INFLIGHT`, then resolves and invokes the tier driver.

Dependencies and integration: Integrates with lifecycle state (`GLOBAL_ExpiryState`, `TransitionedObject`), global tier config (`GLOBAL_TierConfigMgr`), signer error markers, metrics, `tokio::Semaphore`, `uuid`, `sha2`, and `xxhash_rust`.

Risks: The circuit breaker only opens for signer/header failures, so other repeated remote failures are counted but do not short-circuit. `GLOBAL_TierConfigMgr.write()` is held while acquiring/removing through the driver, which may serialize remote deletes more than expected. Several fields and methods are `dead_code` or allow-linted, suggesting incomplete integration.

Test signals: Unit tests cover signer/header error detection and breaker threshold/window recovery. No tests cover versioning matrix journal decisions, worker enqueue failures, or remote driver interactions.
