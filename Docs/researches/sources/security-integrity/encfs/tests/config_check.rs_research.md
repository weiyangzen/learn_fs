# sources/security-integrity/encfs/tests/config_check.rs

Purpose: asserts the `encfs` binary exits nonzero when invoked against a backing directory that lacks a config file.

Important APIs/types/functions: imports the shared `live` helper for unique temp directories and uses `std::process::Command` to run `CARGO_BIN_EXE_encfs`. The single test is `test_missing_config_returns_error`.

Control flow: creates a temp root with `mnt` and `backing`, runs `encfs -f <backing> <mount_point>`, cleans the temp root, then asserts the status is unsuccessful and includes stdout/stderr in the failure message.

State and persistence: creates and removes temporary directories. It does not mount through the live helper or require `ENCFS_LIVE_TESTS`; it invokes the binary directly and expects early validation failure.

Dependencies and integration points: depends on Cargo-provided binary path and the CLI config-loading path. It is an integration test for user-facing error behavior rather than internal config parsing.

Risks: if the binary blocks waiting for input before detecting missing config, the test may hang because `Command::output()` waits for completion. The `env!("CARGO_BIN_EXE_encfs")` fallback is compile-time and can fail outside Cargo integration-test contexts.

Test signals: guards against accidentally creating a new filesystem or mounting successfully when no `.encfs*` config exists.
