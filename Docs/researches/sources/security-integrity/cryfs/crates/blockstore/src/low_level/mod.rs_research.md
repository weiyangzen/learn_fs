
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/mod.rs

## Purpose
This is the public low-level module prelude. It exposes the low-level trait interfaces and selected implementations to the rest of the crate.

## Important APIs, Types, and Functions
- Declares `#[macro_use] mod interface;` so `create_block_data_wrapper!` is available inside implementation modules.
- Re-exports `BlockStoreDeleter`, `BlockStoreReader`, `BlockStoreWriter`, `LLBlockStore`, and `OptimizedBlockStoreWriter`.
- Declares `mod implementations;`.
- Re-exports testutils implementations under `test` or `feature = "testutils"`.
- Re-exports production implementations and integrity config/error types unconditionally.

## Control Flow
No runtime behavior; this file is module wiring and public API shaping.

## State and Persistence Behavior
No state. It controls which stateful backends are available to callers.

## Dependencies and Integration Points
This module is the crate-level import point for `crate::low_level::*` and backs top-level re-exports such as `crate::LLBlockStore`.

## Risks and Edge Cases
Conditional exports mean code using `MockBlockStore`, `SharedBlockStore`, `TrackingBlockStore`, or `TempDirBlockStore` must compile only in test/testutils contexts.

## Test Signals
No direct tests; all low-level implementation and adapter tests depend on this module's re-exports.
