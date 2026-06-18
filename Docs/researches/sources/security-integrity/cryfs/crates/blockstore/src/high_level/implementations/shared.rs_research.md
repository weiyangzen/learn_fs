<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/shared.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/shared.rs

## Purpose
Provides a test/testutils high-level blockstore wrapper that can be cloned by sharing an underlying store through `AsyncDropArc`.

## APIs, Flow, And State
`SharedBlockStore<B>` owns `AsyncDropGuard<AsyncDropArc<B>>`. `new` wraps an underlying async-drop store, and `clone` clones the shared arc into a new async-drop guard. The `BlockStore` implementation delegates all operations, including test cache clearing. `Deref` exposes the underlying store, and `AsyncDrop` delegates to the shared arc.

## Dependencies And Integration
Generic over `BlockStore + AsyncDrop + Debug + Send + Sync` with sendable blocks. Tests instantiate it over `LockingBlockStore<InMemoryBlockStore>` and run generic high-level tests with and without cache flushing.

## Risks And Test Signals
Shared drop semantics are the main concern: clones must not prematurely drop the underlying store, and final async drop must flush/close it exactly when the last guard goes away. The generic suite validates behavior through a shared wrapper but does not exhaustively stress clone lifetimes.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/shared.rs -->
