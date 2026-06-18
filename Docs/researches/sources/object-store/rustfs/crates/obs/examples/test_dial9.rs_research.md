<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/examples/test_dial9.rs -->
# sources/object-store/rustfs/crates/obs/examples/test_dial9.rs

## Purpose
Provides a lightweight manual test for dial9 Tokio runtime telemetry configuration. It verifies default enabled state and prints the env-derived config.

## Important APIs, Types, and Functions
Uses `rustfs_obs::dial9::{Dial9Config, is_enabled}`. `main` checks `is_enabled`, constructs `Dial9Config::from_env`, prints fields such as output directory, file prefix, max size, rotation count, S3 bucket/prefix, and sampling rate, then conditionally asserts default-disabled behavior.

## Control Flow
The example runs three logical checks: default state, config loading, and validation. If dial9 is already enabled through the environment, it skips assertions that assume disabled defaults.

## State and Persistence
No session is initialized and no telemetry file is written. It only reads environment variables and prints results.

## Dependencies and Integration
Integrates with the crate-root dial9 re-export from `telemetry::dial9`. Intended to be invoked through `cargo run -p rustfs-obs --example test_dial9`.

## Risks
It uses console output and assertions rather than structured test harness assertions. Unicode status symbols are present in output, which is harmless for terminals but not important to behavior.

## Test Signals
Manual signal is successful completion and printed PASS lines. It documents env variables needed for enabled dial9 runs and S3 options.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/examples/test_dial9.rs -->
