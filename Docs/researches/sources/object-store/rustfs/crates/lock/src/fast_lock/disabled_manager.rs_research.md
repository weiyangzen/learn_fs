# sources/object-store/rustfs/crates/lock/src/fast_lock/disabled_manager.rs

## Purpose
Implements a no-op fast-lock manager used when locking is disabled via environment configuration, allowing lock call sites to proceed without actual synchronization.

## Important APIs, Types, And Functions
`DisabledLockManager` stores a `LockConfig` only for shape compatibility. It provides `new`, `with_config`, `acquire_lock`, `acquire_read_lock`, `acquire_read_lock_versioned`, `acquire_locks_batch`, metrics/info/count/pool accessors, cleanup methods, and shutdown. Its `LockManager` trait impl marks `is_disabled` as true.

## Control Flow
All acquire paths immediately return disabled `FastLockGuard`s. Batch acquire returns every requested key as successful with no failures. Info and metrics queries return empty values, cleanup returns zero, and shutdown is a no-op.

## State And Persistence
No lock state is stored; guards are no-op disabled guards. There is no persistence or expiry behavior.

## Dependencies And Integration
Uses fast-lock guard, manager trait, metrics, batch/result/config/object types, and `Arc<str>` owners. It plugs into the same `LockManager` trait as the real fast lock manager so higher layers can switch based on env configuration.

## Risks And Edge Cases
The inherent `acquire_read_lock_versioned` creates a write request despite its read-oriented name, which may be harmless while disabled but is semantically suspicious. The trait implementation calls `self.acquire_write_lock` even though this file does not define an inherent `acquire_write_lock`; if the trait has no usable default, this is recursive or fails depending on trait definition and should be checked. Disabled mode removes all mutual exclusion, so it is only safe where external coordination is unnecessary.

## Test Signals
No tests in this file. Coverage should verify disabled acquire returns no-op guards for read/write/batch, `is_disabled` is true, metrics are empty, and the trait `acquire_write_lock` path does not recurse.
