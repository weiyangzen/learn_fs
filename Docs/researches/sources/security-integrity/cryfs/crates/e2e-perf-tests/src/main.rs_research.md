# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/main.rs

## Purpose
Placeholder binary entry point telling users to run tests instead of `cargo run`.

## Important APIs, types, and functions
- `main` prints a short instruction.

## Control flow
Single synchronous print statement.

## State and persistence behavior
No state.

## Dependencies and integration points
Exists because the crate has a binary target; real behavior lives in tests and benches.

## Risks and edge cases
Running the crate binary does not execute performance tests, which could confuse users unless they read the message.

## Test signals
No tests; the signal is the printed message.
