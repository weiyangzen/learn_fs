<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/mod.rs -->
# sources/object-store/rustfs/crates/heal/src/heal/mod.rs

## Purpose

`mod.rs` is the module declaration and public re-export surface for the heal subsystem. It wires the submodules into the crate and exposes the primary manager, erasure healer, resume, and task types to callers.

## Important APIs, types, and functions

Declared modules are `channel`, `erasure_healer`, `event`, `manager`, `progress`, `resume`, `storage`, `task`, and `utils`. Public re-exports include:

- `ErasureSetHealer`
- `HealManager`
- `CheckpointManager`, `ResumeCheckpoint`, `ResumeManager`, `ResumeState`, `ResumeUtils`
- `HealOptions`, `HealPriority`, `HealRequest`, `HealTask`, `HealType`

## Control flow

There is no runtime control flow. The file defines compile-time module topology and which symbols downstream modules can import from `crate::heal`.

## State and persistence behavior

No state or persistence is defined here. Re-exported resume types are the durable state interface, and re-exported task/manager/healer types own runtime behavior elsewhere.

## Dependencies and integration points

The file is the integration point for internal callers that use `crate::heal::{HealManager, HealRequest, ...}` instead of reaching into individual submodules. Adding or removing module declarations changes what code is compiled; adding or removing re-exports changes the public crate-facing API.

## Risks and edge cases

- The module exposes resume internals as public re-exports, so external code can couple to checkpoint/state representation.
- `channel`, `event`, `progress`, `storage`, and `utils` are declared public modules but not all their common types are re-exported here; callers may use mixed import styles.
- Changes here have broad compile impact even though the file is small.

## Test signals

There are no direct tests for this file. Compile tests and downstream imports are the signal: if a module declaration or re-export is wrong, the crate fails to compile. API compatibility checks should watch re-export changes.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/mod.rs -->
