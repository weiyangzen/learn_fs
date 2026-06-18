<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/tests.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/tests.rs

## Purpose
Tests `LockingBlockStore` with generic high-level blockstore conformance and targeted cache/base-store behavior.

## APIs, Flow, And State
`TestFixture` creates `LockingBlockStore<InMemoryBlockStore>` and runs the generic high-level suite with forced cache flush and without. Targeted tests build `MockBlockStore` expectations for create data passthrough, returned random ID consistency, removing an unflushed newly-created block without touching the base store, removing after flush, retrying random IDs when collisions are reported, propagating `exists` errors, and forwarding overhead.

## Dependencies And Integration
Uses `mockall`, `AtomicUsize`, `Arc<Mutex<_>>`, `Overhead`, `Byte`, and high-level test fixtures. It depends on mock low-level store methods such as `exists`, `store`, `remove`, and `overhead`.

## Risks And Test Signals
Some tests note potential flakiness because background pruning could flush entries unexpectedly; a future deterministic pruning control would strengthen them. The suite is a key signal for cache state transitions, especially the regression where a flushed new block must later be considered present in the base store so removal reaches the base store.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/high_level/implementations/locking/tests.rs -->
