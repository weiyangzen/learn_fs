
# sources/security-integrity/cryfs/crates/blockstore/src/tests/low_level/adapter_for_high_level_tests.rs

## Purpose
This adapter lets the high-level common test suite run against low-level `LLBlockStore` implementations by wrapping them in `LockingBlockStore`.

## Important APIs, Types, and Functions
- `FixtureAdapterForHLTests<F, FLUSH_CACHE_ON_YIELD>` stores an `LLFixture`.
- Implements `HLFixture` for any suitable `LLFixture`.
- `ConcreteBlockStore = LockingBlockStore<F::ConcreteBlockStore>`.
- `store()` creates the low-level store through the fixture and wraps it with `LockingBlockStore::new`.
- `yield_fixture()` optionally clears the high-level cache and then delegates to the low-level fixture hook via `store.inner_block_store()`.

## Control Flow
High-level tests call `HLFixture` methods. The adapter builds a low-level store, wraps it in locking/caching high-level semantics, and forwards yield hooks. Cache flushing is controlled by a const generic so tests can be instantiated with or without forced reload behavior.

## State and Persistence Behavior
State belongs to the underlying low-level fixture/store plus `LockingBlockStore` cache state. Flush-on-yield variants test persistence across cache boundaries.

## Dependencies and Integration Points
Bridges `tests::low_level::LLFixture`, high-level `HLFixture`, `LLBlockStore`, and `LockingBlockStore`. Re-exported by `tests/low_level/mod.rs`.

## Risks and Edge Cases
- The adapter tests low-level stores through `LockingBlockStore`, so failures can originate in high-level locking/caching rather than the low-level backend alone.
- `clear_cache_slow().await.unwrap()` panics on cache-clear failure during tests.

## Test Signals
Used to instantiate high-level tests for low-level implementations, ensuring low-level stores can support the high-level locking API contract.
