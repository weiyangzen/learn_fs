# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/env_logger.rs

## Purpose
One-time logger initialization helper for non-benchmark performance tests.

## Important APIs, types, and functions
- Static `INITED: Once`.
- `init()` builds an `env_logger::Builder`, defaults filter level to `Off`, parses environment overrides, and initializes logging once.

## Control flow
`init` uses `Once::call_once` to prevent duplicate logger initialization panics across many tests.

## State and persistence behavior
Process-global logger state is initialized once. No files are written by this helper.

## Dependencies and integration points
Used by test harness code under `#[cfg(not(feature = "benchmark"))]` to keep logs quiet unless environment variables opt in.

## Risks and edge cases
Global logger initialization cannot be undone; tests that need different logger setup must coordinate with this helper.

## Test signals
No direct tests; absence of duplicate-init panics and quiet default logs are the operational signals.
