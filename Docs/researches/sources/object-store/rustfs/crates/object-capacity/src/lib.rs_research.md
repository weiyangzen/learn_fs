<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/object-capacity/src/lib.rs -->
# sources/object-store/rustfs/crates/object-capacity/src/lib.rs

## Purpose
Defines the public module boundary for the `object-capacity` crate. It exposes capacity manager internals, dirty-scope propagation, scan logic, and shared types while keeping the external public re-export surface small.

## Important APIs, Types, and Functions
The crate declares `capacity_manager`, `capacity_scope`, `scan`, and `types` modules. It publicly re-exports `scan_used_capacity_disks` for tooling/benchmarks and `CapacityDiskRef` plus `CapacityScanSummary` for caller-facing scan inputs and outputs.

## Control Flow
There is no runtime control flow in this file. Its behavior is compile-time module wiring and selective re-export.

## State and Persistence
No state is stored here. State lives in `capacity_manager` singletons and scope registries.

## Dependencies and Integration
This file is the integration point external crates use to call the scan API without importing private result types. Making modules public also allows internal RustFS crates to reach manager and scope APIs directly.

## Risks
Because all modules are `pub`, more implementation detail is exposed than the minimal re-exports suggest. Future refactors need to account for downstream users importing module paths directly.

## Test Signals
No tests are defined here; compile-time use by dependent crates and module-level tests in the child modules validate the wiring.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/object-capacity/src/lib.rs -->
