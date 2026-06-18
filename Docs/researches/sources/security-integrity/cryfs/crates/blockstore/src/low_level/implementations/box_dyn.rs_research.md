<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/box_dyn.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/box_dyn.rs

## Purpose
Provides `DynBlockStore`, a dynamic-dispatch wrapper around `Box<dyn LLBlockStore + Send + Sync>`.

## APIs, Flow, And State
`DynBlockStore` implements `BlockStoreReader`, `BlockStoreWriter`, `BlockStoreDeleter`, `AsyncDrop`, and marker `LLBlockStore` by forwarding every call to the boxed trait object. It supports existence/load/count/free-space/overhead/all-blocks queries, create/store writes, remove, and async drop.

## Dependencies And Integration
Used where concrete low-level blockstore types need type erasure while preserving the full low-level store interface.

## Risks And Test Signals
The wrapper adds dynamic dispatch and hides concrete type capabilities such as optimized allocation type. It must be updated if low-level traits gain required methods. There are no local tests in this file; coverage is indirect through consumers of dynamic stores.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/box_dyn.rs -->
