
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/integrity/integrity_data/known_block_versions.rs

## Purpose
This file implements the local integrity ledger used by `IntegrityBlockStore`. It remembers, per block and per client, which block versions have already been observed so that rollback, deletion/reintroduction, and stale-client version attacks can be detected across operations and across process restarts.

## Important APIs, Types, and Functions
- `ClientId` wraps a `NonZeroU32` and is serialized both with `binrw` and `binary_layout`; `0` is reserved for the deleted-block sentinel in `MaybeClientId`.
- `ClientId::generate_random()` creates a random nonzero client id through `rand::rng().random()` into `NonZeroU32`; construction depends on `NonZeroU32` deserialization semantics.
- `MaybeClientId` is either `ClientId(ClientId)` or `BlockWasDeleted`; custom `BinRead`/`BinWrite` encodes `BlockWasDeleted` as integer `0`.
- `BlockVersion` wraps a `u64`, supports `increment()`, and maps to binary-layout `u64`.
- `BlockInfo` is the per-block state: `last_update_client_id` plus `known_block_versions: HashMap<ClientId, BlockVersion>`.
- `BlockInfo::start_increment_version_transaction()` returns `BlockVersionTransaction`, a must-commit-or-cancel RAII transaction used before writes.
- `BlockInfo::check_and_update_version()` validates a read block's `(client_id, version)` against local state and emits `IntegrityViolationError::RollBack` on rollback-like transitions.
- `KnownBlockVersions` owns `integrity_violation_in_previous_run: AtomicBool` and an `Arc<LockableHashMap<BlockId, BlockInfo>>`.
- `KnownBlockVersions::load`, `load_or_default`, and async `save` bridge this live state to `KnownBlockVersionsSerialized`.
- `KnownBlockVersions::lock_block_info()` returns an owned async lock guard for a single block id; callers mutate block integrity state under that guard.

## Control Flow
Write paths call `start_increment_version_transaction()`, derive the next version for the current client from the local map, and later either `commit()` or `cancel()`. Commit updates both `last_update_client_id` and the client-version entry; cancellation drops the pending mutation. The transaction `Drop` panics through `safe_panic!` if neither action was taken, making incomplete write protocol violations visible.

Read paths call `check_and_update_version()`. First observations for a client insert the observed version and set `last_update_client_id`. Existing client observations reject lower versions. When returning to a different previously seen client, equal versions are rejected too, so a client switch must use a strictly newer version than the last version observed for that client. Same-client equal versions remain valid for repeated reads. Deleted blocks behave like switching from `BlockWasDeleted`; reintroducing an old client version must be strictly newer than the remembered version.

## State and Persistence Behavior
`KnownBlockVersions` is persisted only through `save(self, file_path)`, consuming the live state and converting it into `KnownBlockVersionsSerialized`. The persisted data includes the previous-run violation flag, all `(client, block) -> version` entries, and each block's last-update/deleted marker. Missing state files load as default empty ledgers. `existing_blocks()` returns keys with entries or locked entries from the lockable map; notably, its name is broader than `BlockInfo::block_is_expected_to_exist()` and can include deleted entries or currently locked entries.

## Dependencies and Integration Points
This module depends on `lockable` for per-block async locking, `binrw` and `binary_layout` for binary formats, CryFS binary helpers for `NonZeroU32`, and `IntegrityViolationError` for rollback reporting. It is re-exported by `integrity_data/mod.rs` and consumed directly by `IntegrityBlockStore` for load, store, create, remove, and missing-block checks.

## Risks and Edge Cases
- `ClientId::generate_random()` has a TODO questioning zero generation; because `NonZeroU32` cannot hold zero, this must be audited against the `rand` distribution implementation.
- `BlockVersion::increment()` can overflow `u64`; no checked arithmetic is present.
- `KnownBlockVersions::existing_blocks()` uses `keys_with_entries_or_locked()`, and a TODO questions whether locked keys should count as existing. This matters for `IntegrityBlockStore::all_blocks()` missing-block detection.
- The rollback rule intentionally allows first-time observations from new clients with lower versions, because no local prior for that client exists. Security depends on prior observation history.
- Persistence safety depends on callers completing async drop; if `KnownBlockVersions` is not saved, local anti-rollback history is lost.

## Test Signals
The tests cover new/empty blocks, per-client and per-block versions, increasing and decreasing version checks, deletion markers, transaction commit/cancel/panic behavior, same-client versus different-client rollback rules, current version lookup, existing-block listing, save/load round trips, and base64-encoded backward-compatibility fixtures for older serialized state.
