<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/profiler.rs -->
# sources/object-store/rustfs/crates/config/src/constants/profiler.rs

## Purpose
Defines environment names and defaults for RustFS CPU and memory profiling controls.

## Important APIs, types, and functions
Exports global profiling enable, CPU mode/frequency/interval/duration keys, jemalloc memory periodic/interval keys, output directory key, and defaults: profiling disabled, CPU mode `off`, 100 Hz sampling, 300-second interval, 60-second duration, memory periodic disabled, output dir `.`.

## Control flow
No runtime logic; profiler initialization reads these constants and starts continuous/periodic profilers if enabled.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with CPU profiler, jemalloc memory profiling, filesystem output paths, and operator debugging workflows.

## Risks and edge cases
Profiling can create sensitive or large output files and add runtime overhead. Defaults are safe/off, but invalid mode strings must be rejected by downstream parser.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended. Profiler tests should cover disabled default, mode parsing, periodic scheduling, output directory validation, and memory profiler feature availability.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/profiler.rs -->
