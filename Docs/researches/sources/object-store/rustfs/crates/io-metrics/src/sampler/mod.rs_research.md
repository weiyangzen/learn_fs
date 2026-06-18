<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/sampler/mod.rs -->
## sources/object-store/rustfs/crates/io-metrics/src/sampler/mod.rs

### Purpose
Defines the sampler module surface and re-exports process and platform snapshot APIs.

### Important APIs, Types, And Functions
Declares `pub mod process` and `pub mod system`. Re-exports `ProcessResourceSnapshot`, `ProcessStatusSnapshot`, `ProcessSystemSnapshot`, `snapshot_process_resource`, `snapshot_process_resource_and_system`, `snapshot_process_system`, and `snapshot_process_platform`.

### Control Flow
No runtime control flow beyond module wiring and re-export resolution.

### State And Persistence
No state in this module; state resides in `process.rs` and `process_lock_metrics.rs`.

### Dependencies And Integration Points
Serves as the public sampler namespace and is re-exported from `lib.rs`.

### Risks
Because it re-exports both process-level and platform-level snapshot functions, API consumers should understand that some fields are OS-dependent or optional/defaulted.

### Test Signals
No tests in this file; coverage is through submodule tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/io-metrics/src/sampler/mod.rs -->
