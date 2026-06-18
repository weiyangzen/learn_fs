<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/runtime.rs -->
# sources/object-store/rustfs/crates/config/src/constants/runtime.rs

## Purpose
Defines Tokio runtime, telemetry, transition worker, allocator reclaim, file-cache reclaim, test-injection, and small-object seek support configuration constants.

## Important APIs, types, and functions
Runtime knobs include worker/blocking thread counts, thread stack/keepalive/name, queue/event intervals, I/O events per tick, RNG seed, and Dial9 telemetry output/S3/sampling settings. Transition constants set worker caps, queue capacity, send timeout, and test fault injection envs. Allocator/file-cache reclaim and object seek threshold defaults are also exported.

## Control flow
No local execution; startup/runtime builders and background services consume these constants.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with Tokio runtime construction, telemetry logging/upload, lifecycle transition queues, IAM bootstrap test hooks, allocator reclaim loops, object file-cache hints, and small-object seek buffering.

## Risks and edge cases
Thread and blocking defaults strongly affect resource use. Test-only env vars must not be exposed as production behavior. Seek support threshold has a downstream hard cap, so parser/runtime docs must stay consistent. Telemetry paths can create sizable logs.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended. Runtime tests should cover env parsing bounds, transition queue backpressure, fault-injection gating, allocator reclaim cadence, and seek threshold cap behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/runtime.rs -->
