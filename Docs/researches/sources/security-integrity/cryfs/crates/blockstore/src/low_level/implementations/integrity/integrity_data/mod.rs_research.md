
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/integrity/integrity_data/mod.rs

## Purpose
`IntegrityData` is the owning wrapper around `KnownBlockVersions`. It represents the local integrity state file for one CryFS client and provides the API used by `IntegrityBlockStore` to lock per-block ledger entries, query previous violations, and save the state on async drop.

## Important APIs, Types, and Functions
- Re-exports `IntegrityViolationError`, `BlockInfo`, `BlockVersion`, `BlockVersionTransaction`, `ClientId`, `KnownBlockVersions`, and `MaybeClientId`.
- `IntegrityData::new(state_file_path, my_client_id)` loads `KnownBlockVersions` from the path or creates a default ledger, returning `AsyncDropGuard<Self>`.
- `my_client_id()` exposes the client id used when writing new block headers.
- `lock_block_info(block_id)` delegates to `KnownBlockVersions::lock_block_info()`.
- `integrity_violation_in_previous_run()` and `set_integrity_violation_in_previous_run()` bridge the persistent violation latch.
- `existing_blocks()` returns the block ids known by the underlying ledger.
- `AsyncDrop::async_drop_impl()` takes the ledger out of `Option` and persists it.

## Control Flow
Construction reads the integrity state before the blockstore wrapper is made usable. Normal operations lock block state through immutable `&self`, relying on interior locking in `KnownBlockVersions`. On destruction, `known_block_versions` is `take()`n so it can be consumed by `save()`. Accessors panic with "Object is currently being destructed" if used after destruction begins.

## State and Persistence Behavior
The state file path and client id are immutable after construction. Ledger persistence happens on async drop, not after every block operation. The module has a TODO noting that file locking is missing, so multiple CryFS processes could open and mutate the same state file concurrently. Another TODO questions whether `IntegrityData` and `KnownBlockVersions` should remain separate serialization layers.

## Dependencies and Integration Points
The module depends on `AsyncDropGuard` for lifecycle-managed persistence, `lockable` guard types for per-block locking, and `KnownBlockVersionsSerialized` indirectly through `KnownBlockVersions`. It is an internal module of `IntegrityBlockStore`.

## Risks and Edge Cases
- State durability is async-drop based; crashes or missed async-drop calls may lose recent integrity updates.
- No OS-level file locking is used, creating possible multi-process races and last-writer-wins corruption.
- During destruction, any lingering lock users can collide with the `Option::take()` lifecycle.

## Test Signals
Tests instantiate `IntegrityData` in a tempdir, use helper `clientid()` and `version()`, set versions under block locks, and assert per-client/per-block version separation plus rejection of decreasing versions.
