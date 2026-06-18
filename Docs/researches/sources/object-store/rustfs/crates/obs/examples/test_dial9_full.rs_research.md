<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/examples/test_dial9_full.rs -->
# sources/object-store/rustfs/crates/obs/examples/test_dial9_full.rs

## Purpose
Exercises the full dial9 lifecycle, including session initialization, async workload generation, and guard drop cleanup.

## Important APIs, Types, and Functions
Imports `Dial9Config`, `init_session`, and `is_enabled`. The async `main` reads config, calls `init_session().await`, checks `guard.is_active()`, spawns three Tokio tasks that sleep and print iterations, then drops the guard.

## Control Flow
If dial9 is disabled, the example prints enable instructions and exits successfully. When enabled, it reports config, initializes a session, runs concurrent async tasks to generate runtime activity, and tests cleanup by dropping the guard. `Ok(None)` is treated as a nonfatal writer failure case.

## State and Persistence
When enabled and initialized, dial9 likely writes telemetry artifacts under the configured output directory. The guard owns session lifecycle and cleanup.

## Dependencies and Integration
Depends on Tokio task spawning and time, plus the crate dial9 module. It is useful for validating dial9 integration in a real runtime rather than just config parsing.

## Risks
The summary prints PASS lines even if `init_session` returns an error; this is suitable for exploratory examples but could mislead if used as CI. It does not inspect output files.

## Test Signals
Manual signals include config printout, session initialization result, guard activity state, task completion, and absence of runtime errors.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/examples/test_dial9_full.rs -->
