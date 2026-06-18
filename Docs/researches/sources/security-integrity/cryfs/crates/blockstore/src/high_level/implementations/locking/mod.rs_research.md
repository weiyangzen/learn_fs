<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/mod.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/mod.rs

## Purpose
Module hub for the high-level locking blockstore implementation.

## APIs, Flow, And State
Declares the internal `cache` module, exposes `LockingBlock` and `LockingBlockStore`, and includes locking tests under `cfg(test)`.

## Dependencies And Integration
Re-exported by `high_level::implementations` and ultimately by the crate root as the main high-level blockstore implementation.

## Risks And Test Signals
No runtime logic is present here. The important boundary is keeping cache internals private while exposing only the block and store wrappers.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/mod.rs -->
