<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/lib.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/lib.rs

## Purpose
Crate root for `cryfs-blockstore`, exposing block IDs, high-level and low-level storage APIs, implementations, overhead utilities, and test helpers.

## APIs, Flow, And State
The crate re-exports `BlockId`, `BLOCKID_LEN`, `RemoveResult`, `TryCreateResult`, high-level `Block`, `BlockStore`, `LockingBlockStore`, and many low-level implementations such as encrypted, compressed, in-memory, on-disk, integrity, dynamic, read-only, and optimized writer types. Under test/testutils it re-exports high-level and low-level tracking/shared/mock/tempdir utilities and the `tests` module. A static assertion ensures `byte_unit::Byte` has the expected `u64` size.

## Dependencies And Integration
Connects internal modules `block_id`, `utils`, `high_level`, `low_level`, and `overhead`. `cryfs_version::assert_cargo_version_equals_git_version!()` enforces version consistency.

## Risks And Test Signals
The root public surface is broad, so accidental re-export changes can affect downstream crates. The static Byte-size assertion protects storage calculations from feature-induced type-width changes.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/lib.rs -->
