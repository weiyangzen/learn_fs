<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/zero_copy.rs -->
# sources/object-store/rustfs/crates/config/src/constants/zero_copy.rs

## Purpose
Defines environment names and defaults for zero-copy reads and optional Linux Direct I/O.

## Important APIs, types, and functions
`ENV_OBJECT_ZERO_COPY_ENABLE` defaults true for mmap/optimized reads. `ENV_OBJECT_DIRECT_IO_ENABLE` defaults false. `ENV_OBJECT_DIRECT_IO_THRESHOLD` defaults to 128 MiB.

## Control flow
No executable logic. Object I/O layers decide whether platform support, file size, and failure behavior allow mmap or O_DIRECT.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with Unix mmap reads, non-Unix fallback reads, Linux O_DIRECT paths, object read performance tuning, and deployment-specific large-file workloads.

## Risks and edge cases
Zero-copy default on requires robust fallback if mmap fails. Direct I/O has alignment and workload caveats and is off by default. Threshold parsing must be in bytes and prevent tiny files from using O_DIRECT.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended. I/O tests should cover mmap success/fallback, non-Unix fallback, O_DIRECT thresholding/alignment, and operator env overrides.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/zero_copy.rs -->
