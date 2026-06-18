# sources/storage-engines/tikv/components/log_wrappers/Cargo.toml

## Purpose
This manifest defines the private `log_wrappers` crate, which provides logging wrappers for third-party types and redacted key/value formatting.

## Important APIs, Types, and Functions
Dependencies include `atomic`, `hex`, `online_config`, `protobuf`, `serde`, `slog`, `slog-term`, `toml`, and `tikv_alloc`. These map directly to redaction state, hex encoding, online-config conversion, protobuf redaction levels, and test logging.

## Control Flow
No runtime control flow exists in the manifest.

## State and Persistence Behavior
The manifest has no runtime state, but the crate it defines controls process-global logging redaction state.

## Dependencies and Integration Points
`online_config` allows config-driven redaction changes; `protobuf` shares redaction marker semantics with generated protobuf logging; `slog` is TiKV's structured logging stack.

## Risks
Logging code is security-sensitive. Dependency changes that alter redaction parsing or marker formatting could expose user data or break expected log output.

## Test Signals
Tests are in `src/lib.rs` and `src/test_util.rs` support code.
