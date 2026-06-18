
# sources/security-integrity/cryfs/crates/blockstore/src/tests/low_level/fixture.rs

## Purpose
Defines `LLFixture`, the fixture contract for instantiating the common low-level blockstore test suite against concrete `LLBlockStore` implementations.

## Important APIs, Types, and Functions
- `LLFixture::ConcreteBlockStore` must implement `LLBlockStore + Send + Sync`.
- `new()` constructs fixture state.
- `store()` asynchronously constructs an `AsyncDropGuard` for the concrete low-level store.
- `yield_fixture(&self, store)` is an async hook between test operations and assertions.

## Control Flow
Low-level test macros create a fixture, request a store, run low-level operations, call the yield hook between phases, and explicitly async-drop the store. Fixture state can own tempdirs, shared stores, or other setup resources.

## State and Persistence Behavior
No state in the trait itself. Implementations define resource lifetime and optional flushing behavior.

## Dependencies and Integration Points
Depends on crate `LLBlockStore` and CryFS `AsyncDropGuard`. Re-exported by `tests/low_level/mod.rs` and consumed by common low-level tests plus high-level adapter tests.

## Risks and Edge Cases
- The TODO asks whether low-level implementations actually need `yield_fixture()`.
- Implementors must preserve backing resources until all stores created for a test are dropped.

## Test Signals
The fixture is the generic entry point for the low-level test macro suite; no direct local tests.
