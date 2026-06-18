<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/examples/test_dial9_simple.rs -->
# sources/object-store/rustfs/crates/obs/examples/test_dial9_simple.rs

## Purpose
Provides the smallest dial9 configuration smoke test. It reads environment state, prints the parsed config, and confirms base path calculation.

## Important APIs, Types, and Functions
Uses `Dial9Config::from_env`, `Dial9Config::base_path`, and `is_enabled`. It prints enabled flag, output directory, file prefix, max file size, rotation count, and sampling rate.

## Control Flow
The async main performs three sequential checks: environment enabled state, config loading, and base-path calculation. It does not initialize a telemetry session.

## State and Persistence
No files are written. Runtime state is limited to local config values parsed from environment variables.

## Dependencies and Integration
Depends on the dial9 module re-export from `rustfs_obs`. It can be run with env variables to confirm parser behavior before running the full session example.

## Risks
It is not a real integration test of writer creation, rotation, S3 upload, or runtime event capture. It only proves the config API can be called.

## Test Signals
Successful completion and printed config values are the expected signal. The example documents env vars for enabling full dial9 functionality.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/examples/test_dial9_simple.rs -->
