
# sources/security-integrity/cryfs/crates/blockstore/src/tests/high_level/tests.rs

## Purpose
This file defines the common high-level `LockingBlockStore`/`BlockStore` behavior suite and macros to instantiate it for concrete high-level fixtures.

## Important APIs, Types, and Functions
- `instantiate_highlevel_blockstore_specific_tests!` creates modules for create, remove, resize, data, overwrite, and overhead tests.
- `_instantiate_highlevel_blockstore_specific_tests!` recursively emits `#[tokio::test]` functions that call the shared async test functions.
- `assert_block_is_usable()` mutates a block's full data region, drops it, reloads it, and checks persistence.
- Test modules:
  - `create`: created block ids differ.
  - `remove`: modified loaded blocks can be removed.
  - `resize`: zero/nonzero blocks can grow, shrink, and become zero while remaining usable.
  - `data`: partial writes over several offsets/counts preserve unaffected ranges.
  - `overwrite`: overwriting while a block is loaded blocks until the guard is dropped, then succeeds.
  - `usable_block_size_from_physical_block_size`: overhead conversions round trip.

## Control Flow
The instantiation macro generates nested modules and per-test Tokio functions. Individual tests use `HLFixture` to create a store, call `yield_fixture()` between mutation and assertion phases, and explicitly async-drop the store. The overwrite blocking test uses `Arc`, `tokio::spawn`, sleeps, and `is_finished()` to assert lock behavior.

## State and Persistence Behavior
Tests assume high-level block guards flush changes on drop or store lifecycle as appropriate. `yield_fixture()` allows implementations to flush caches/reopen state between steps. Data tests validate both immediate in-memory views and reload-after-drop persistence.

## Dependencies and Integration Points
Depends on `HLFixture`, high-level `BlockStore` and `Block` traits, `RemoveResult`, test data helpers, and `assert_data_range_eq`. The comments note that many low-level behaviors are tested by adapting high-level stores to low-level tests.

## Risks and Edge Cases
- The overwrite blocking tests use fixed 100 ms sleeps, which can be timing-sensitive on slow or overloaded systems.
- Several TODOs remain for `Block::block_id()`, `data()` identity, `flush()`, and additional locking behaviors.
- Tests rely on explicit async drops; leaks can hide persistence issues.

## Test Signals
This file is itself the high-level test signal. It covers ids, remove-after-modification, resize data usability, partial write preservation, write persistence after loading, overwrite locking, and overhead arithmetic.
