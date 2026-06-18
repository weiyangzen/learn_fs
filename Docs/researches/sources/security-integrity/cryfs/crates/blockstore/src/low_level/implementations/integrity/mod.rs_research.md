
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/integrity/mod.rs

## Purpose
`IntegrityBlockStore` wraps a low-level blockstore and adds CryFS integrity checks. It prepends an integrity header to every physical block, updates local anti-rollback state on successful writes/reads/removes, detects wrong block ids, rollbacks, reintroduced deleted blocks, and optionally missing blocks.

## Important APIs, Types, and Functions
- `block_layout` defines the per-block header: `format_version_header: u16`, `block_id`, `last_update_client_id`, `block_version`, then user data.
- `AllowIntegrityViolations` controls whether detected violations are fatal or only logged.
- `MissingBlockIsIntegrityViolation` distinguishes single-client-style stores from multi-client stores where another authorized client may have deleted a block.
- `IntegrityConfig` stores those flags plus an `on_integrity_violation` callback.
- `IntegrityBlockStore::new()` loads `IntegrityData`, checks the persistent prior-violation latch, and may refuse to open.
- `BlockStoreReader` implementation checks headers on `load()` and performs missing-block reconciliation in `all_blocks()`.
- `BlockStoreDeleter::remove()` marks a block deleted after the underlying remove succeeds.
- `OptimizedBlockStoreWriter` implementation allocates prefix-capable data and commits/cancels `BlockVersionTransaction` around underlying writes.
- `_integrity_violation_detected()` centralizes allow/log/fail behavior and latches previous-run violations.
- `_prepend_header()` writes the header and returns the version transaction.
- `_check_and_remove_header()` validates physical data, strips the integrity header, and updates the version ledger.

## Control Flow
Construction first tries to load local integrity data; if that fails, it drops the underlying store and returns `InvalidLocalIntegrityState`. If a previous violation is latched and violations are not allowed, it async-drops both integrity data and underlying store, then returns `IntegrityViolationInPreviousRun`.

`load()` locks the target block's `BlockInfo`, loads from the underlying store, handles missing blocks according to config, creates unknown state for newly seen blocks, validates format and id headers, reads client/version, strips the header, and only then updates the version ledger.

`all_blocks()` either delegates directly or, when missing blocks are violations, collects underlying block ids, snapshots expected block ids from integrity state, removes physically present ids, then re-locks/re-checks each missing candidate with `exists()` to reduce race false positives. Remaining missing ids become an `IntegrityViolationError::MissingBlocks`.

Writes call `_prepend_header()` while holding the block lock. `try_create_optimized()` commits only on `SuccessfullyCreated`, cancels on already-existing or error. `store_optimized()` commits only on successful underlying store. `remove()` marks deleted after the underlying remove call returns without error, regardless of whether the remove result says the block actually existed.

## State and Persistence Behavior
Integrity state is persisted by `IntegrityData` on async drop. Per-block physical state stores the client id and version inside each block file/object. Detected fatal integrity violations set the persistent prior-run latch so future opens fail until the integrity file is deleted or violations are allowed. `overhead()` adds the integrity header size to the underlying store overhead.

## Dependencies and Integration Points
This wrapper composes with any `LLBlockStore + OptimizedBlockStoreWriter`. It uses `binary_layout` for block headers, `byte_unit::Byte` and `Overhead` for size accounting, `futures` for stream and missing-block concurrency, and `IntegrityData` for persistent local state. It is exported by `implementations/mod.rs` and `low_level/mod.rs`.

## Risks and Edge Cases
- Missing-block scanning is collection-based and has documented race-condition TODOs around concurrent remove/update operations.
- `remove()` records deletion after successful call even when `RemoveResult::NotRemovedBecauseItDoesntExist`; this is intentional for anti-reintroduction but can record state for never-seen blocks.
- Violation latching is saved on async drop, so a fatal error followed by crash before drop could lose the latch.
- Header format mismatch is an ordinary error, not routed through `_integrity_violation_detected()`.
- `AllowViolations` still updates local ledger after accepting suspicious data, which can affect later observations.
- Initialization uses `unwrap()` inside async-drop joins for the previous-violation path.

## Test Signals
Generic tests instantiate common low-level tests across allow/missing-block modes and verify overhead conversion. Specialized tests simulate rollback, same-client version decrease, client switching, deleted-block reintroduction, missing block load/listing, and wrong block id headers, checking both fatal and allow-violation configurations.
