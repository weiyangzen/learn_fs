
# sources/security-integrity/cryfs/crates/blockstore/src/tests/low_level/mod.rs

## Purpose
This module wires together the low-level common test fixture, high-level adapter, and test suite exports.

## Important APIs, Types, and Functions
- Module docs describe common tests for `crate::LLBlockStore` implementations.
- Declares `fixture` and re-exports `LLFixture`.
- Declares `adapter_for_high_level_tests` and re-exports `FixtureAdapterForHLTests`.
- Exposes `pub mod tests`.

## Control Flow
No runtime behavior. It organizes and re-exports test infrastructure.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Imported by concrete low-level implementation tests to implement fixtures or instantiate macro suites. Also supports high-level testing through `FixtureAdapterForHLTests`.

## Risks and Edge Cases
Changing this module's re-exports would affect many implementation test modules that import through `crate::tests::low_level`.

## Test Signals
Indirectly exercised by every low-level blockstore implementation test instantiation.
