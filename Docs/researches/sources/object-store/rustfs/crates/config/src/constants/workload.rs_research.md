<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/workload.rs -->
# sources/object-store/rustfs/crates/config/src/constants/workload.rs

## Purpose
Defines environment names and defaults for workload buffer sizing.

## Important APIs, types, and functions
Exports `ENV_RUSTFS_BUFFER_MIN_SIZE`, `ENV_RUSTFS_BUFFER_MAX_SIZE`, `ENV_RUSTFS_BUFFER_DEFAULT_SIZE`, and defaults 64 KiB minimum, 1 MiB maximum, and 256 KiB unknown-size buffer.

## Control flow
No runtime flow besides unit tests asserting constants and byte math.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with object/read buffering and workload profile selection code that imports `KI_B` and `MI_B` from the config crate.

## Risks and edge cases
Misordered min/default/max parsing downstream can cause inefficient buffering or memory spikes. Constants depend on crate-level KiB/MiB definitions staying stable.

## Test signals
Unit tests pin byte values and env names. Runtime tests should verify env overrides are clamped and selected buffers respect min/default/max relationships.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/workload.rs -->
