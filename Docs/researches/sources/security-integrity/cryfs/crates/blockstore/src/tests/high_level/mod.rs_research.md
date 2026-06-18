
# sources/security-integrity/cryfs/crates/blockstore/src/tests/high_level/mod.rs

## Purpose
This module wires together the high-level test fixture, adapter, and test suite exports.

## Important APIs, Types, and Functions
- Declares `adapter_for_low_level_tests` and re-exports `BlockStoreToLLBlockStoreAdapter` and `FixtureAdapterForLLTests`.
- Declares `fixture` and re-exports `HLFixture`.
- Exposes `pub mod tests`.

## Control Flow
No runtime behavior. It is test module organization.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Imported by concrete blockstore tests that need to implement `HLFixture` or instantiate common high-level tests. The adapter re-export also enables running low-level tests against high-level stores.

## Risks and Edge Cases
Changing re-exports here can break test modules that import through `crate::tests::high_level`.

## Test Signals
Indirectly exercised by all high-level test instantiations.
