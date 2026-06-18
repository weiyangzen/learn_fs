
# sources/security-integrity/cryfs/crates/blockstore/src/tests/high_level/adapter_for_low_level_tests.rs

## Purpose
This adapter lets the low-level common test suite run against high-level `BlockStore` implementations by wrapping a high-level store in an `LLBlockStore` facade.

## Important APIs, Types, and Functions
- `BlockStoreToLLBlockStoreAdapter<B>(AsyncDropGuard<B>)` owns a high-level blockstore.
- `new(store)` wraps the high-level store.
- `clear_cache_slow()` forwards to the high-level store for fixtures that flush between assertions.
- Implements `BlockStoreReader`: `exists()` loads and checks `Option`, `load()` extracts block data, `num_blocks`, `estimate_num_free_bytes`, `overhead`, and `all_blocks` delegate.
- Implements `BlockStoreDeleter::remove()` via `remove_by_id`.
- Implements `BlockStoreWriter::try_create()` via high-level `try_create`, and `store()` via `overwrite`.
- Implements `AsyncDrop` and marker `LLBlockStore`.
- `FixtureAdapterForLLTests<F, FLUSH_CACHE_ON_YIELD>` adapts an `HLFixture` to an `LLFixture`.

## Control Flow
The low-level suite calls the adapter's low-level methods. For reads, high-level loaded block objects are converted to cloned `Data`. For writes, `&[u8]` is copied into a `Data` value and submitted to the high-level API. Fixture `yield_fixture()` optionally clears the high-level cache before delegating to the wrapped fixture's yield hook.

## State and Persistence Behavior
State is owned by the wrapped high-level store. The adapter is lifecycle-managed by `AsyncDropGuard` and drops the inner store on async drop.

## Dependencies and Integration Points
Bridges `tests::high_level::HLFixture`, `tests::low_level::LLFixture`, the high-level `BlockStore` trait, and low-level blockstore traits. It is re-exported by `tests/high_level/mod.rs`.

## Risks and Edge Cases
- `exists()` is implemented by loading the full block, which may be heavier than native low-level existence checks.
- `load()` clones block data out of the high-level block, so mutation semantics differ from holding a high-level block guard.
- Adapter writes go through high-level locking/cache behavior, so it tests the high-level facade as a low-level store rather than raw persistence.

## Test Signals
Used by macro-based suites to apply low-level tests to high-level stores. Flush-on-yield variants exercise behavior across cache clears.
