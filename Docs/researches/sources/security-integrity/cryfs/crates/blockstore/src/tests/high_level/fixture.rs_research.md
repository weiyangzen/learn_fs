
# sources/security-integrity/cryfs/crates/blockstore/src/tests/high_level/fixture.rs

## Purpose
Defines `HLFixture`, the fixture contract for instantiating the common high-level `BlockStore` test suite against concrete implementations.

## Important APIs, Types, and Functions
- `HLFixture::ConcreteBlockStore` must implement `BlockStore + AsyncDrop + Debug + Send + Sync + 'static`.
- `new()` creates fixture state.
- `store()` asynchronously creates an `AsyncDropGuard` for the concrete store.
- `yield_fixture(&self, store)` is an async hook used between test actions and assertions.

## Control Flow
Test macros construct a fixture, request a store, run operations, call `yield_fixture()` between phases, and explicitly async-drop the store. Implementations can use the fixture object to hold tempdirs or other RAII resources for the whole test.

## State and Persistence Behavior
No state in the trait itself. Fixture implementations decide how long backing resources live. The design keeps the fixture alive for the duration of each test.

## Dependencies and Integration Points
Depends on the crate high-level `BlockStore` trait and `cryfs_utils::async_drop`. Re-exported by `tests/high_level/mod.rs` and consumed by high-level test macros plus adapters.

## Risks and Edge Cases
- Implementors must ensure `yield_fixture()` does not invalidate active block guards unless the test expects that.
- Tests rely on explicit `async_drop()` calls; fixture implementations should make cleanup robust.

## Test Signals
The trait itself has no tests; every high-level common test is parameterized over it.
