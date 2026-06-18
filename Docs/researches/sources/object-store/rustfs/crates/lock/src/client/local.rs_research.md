# sources/object-store/rustfs/crates/lock/src/client/local.rs

## Purpose
Implements a local `LockClient` backed by the fast in-process global lock manager, with sharded storage of RAII guards so locks remain held until explicitly released.

## Important APIs, Types, And Functions
`LocalClient` stores guard shards, a shard mask, and optional injected `GlobalLockManager`. Constructors include `new`, `with_shard_count`, and `with_manager`. `get_lock_manager` returns the injected manager or global singleton. `get_shard_index/get_shard` map lock ids to shard maps. The `LockClient` impl covers acquire, release, refresh, force release, check status, stats, close, and online/local checks.

## Control Flow
`acquire_lock` translates generic `LockRequest` into `ObjectLockRequest::new_write` for exclusive or `new_read` for shared, preserving acquire timeout. On success it stores the returned `FastLockGuard` under the request lock id in the appropriate shard and returns acquired `LockInfo`. Timeout/conflict fast-lock errors become failure `LockResponse`s. `release` removes and drops the stored guard, triggering actual lock release.

## State And Persistence
State is in-memory guard storage split across 64 shards by default. Locks do not expire automatically locally; `refresh` is a no-op success and `check_status` fabricates current timing metadata from stored guards.

## Dependencies And Integration
Uses crate-level fast lock types, `GlobalLockManager`, generic lock DTOs, Tokio `RwLock`, and `HashMap`. `ClientFactory::create_local` returns this implementation as `Arc<dyn LockClient>`. Distributed locks can compose local clients for quorum simulations.

## Risks And Edge Cases
`with_shard_count` panics if the count is not a power of two. `check_status` derives resource from `lock_id.resource` and uses default metadata/priority rather than the original request fields. TTL is recorded in `LockInfo` but not enforced by this client. `get_stats` returns defaults rather than fast-lock manager metrics.

## Test Signals
No direct tests in this file; behavior is covered indirectly through distributed and namespace tests that use local clients and fast-lock guards.
