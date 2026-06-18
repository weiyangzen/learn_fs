
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/shared.rs

## Purpose
`SharedBlockStore` is a testutils wrapper that allows multiple owners to share one async-drop-managed underlying blockstore through `AsyncDropArc`. It supports tests that need one component to mutate the raw underlying store while another wrapper observes integrity/encryption behavior.

## Important APIs, Types, and Functions
- `SharedBlockStore::new(underlying)` wraps an `AsyncDropGuard<B>` in `AsyncDropArc`.
- `SharedBlockStore::clone(&AsyncDropGuard<Self>)` creates another guarded wrapper sharing the same underlying store.
- Implements `BlockStoreReader`, `BlockStoreDeleter`, `OptimizedBlockStoreWriter`, `AsyncDrop`, `LLBlockStore`, and `Deref<Target = B>`.

## Control Flow
All blockstore methods delegate directly to `underlying_store`. Async drop calls `async_drop()` on the `AsyncDropArc`, so actual underlying destruction is coordinated by the shared async-drop mechanism. `Deref` exposes the underlying store for tests.

## State and Persistence Behavior
The wrapper itself stores only the shared async-drop reference. Persistence and state are owned by the underlying blockstore.

## Dependencies and Integration Points
Depends on `cryfs_utils::async_drop::{AsyncDropArc, AsyncDropGuard}`. It is used in integrity specialized tests to inspect and tamper with raw blocks below `IntegrityBlockStore`.

## Risks and Edge Cases
- Intended only for test code; exposing `Deref` to the underlying store can break abstraction boundaries.
- Async-drop correctness depends on all shared wrappers being dropped.

## Test Signals
The module runs the common low-level suite using `SharedBlockStore<InMemoryBlockStore>` and verifies zero overhead conversions.
