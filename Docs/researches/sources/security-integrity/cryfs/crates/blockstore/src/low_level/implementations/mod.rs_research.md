
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/mod.rs

## Purpose
This module is the implementation registry for low-level blockstore backends and wrappers. It declares submodules and re-exports the public implementation types used by the rest of the crate.

## Important APIs, Types, and Functions
- Always exported: `CompressingBlockStore`, `EncryptedBlockStore`, `InMemoryBlockStore`, `IntegrityBlockStore`, `OnDiskBlockStore`, `ReadOnlyBlockStore`, and `DynBlockStore`.
- Integrity configuration/error exports: `AllowIntegrityViolations`, `ClientId`, `IntegrityBlockStoreInitError`, `IntegrityConfig`, `IntegrityViolationError`, `MissingBlockIsIntegrityViolation`.
- Testutils-gated exports: `MockBlockStore`, `SharedBlockStore`, `ActionCounts`, `TrackingBlockStore`, `TempDirBlockStore`.

## Control Flow
There is no runtime control flow; it is compile-time module wiring. Conditional compilation hides mock/shared/tracking/tempdir utilities unless running tests or enabling `testutils`.

## State and Persistence Behavior
No direct state. It controls visibility of stateful modules such as on-disk and integrity implementations.

## Dependencies and Integration Points
This file is consumed by `low_level/mod.rs`, which re-exports these implementation types at the crate low-level API boundary.

## Risks and Edge Cases
Re-export changes here affect downstream imports. Test-only wrappers are intentionally unavailable in normal production builds unless `feature = "testutils"` is enabled.

## Test Signals
No direct tests; coverage is indirect through each implementation's own test modules and common blockstore test macros.
