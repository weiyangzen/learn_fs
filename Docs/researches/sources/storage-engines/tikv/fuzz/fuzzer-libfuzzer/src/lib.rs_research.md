# sources/storage-engines/tikv/fuzz/fuzzer-libfuzzer/src/lib.rs

## Purpose
Placeholder library for the libFuzzer package so Cargo can load the package before generated binary harnesses exist.

## Important APIs, Types, and Functions
No public API; comments point to dynamic generation from `fuzz/cli.rs`.

## Control Flow
No runtime control flow.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Complements libFuzzer template-based generated binaries.

## Risks
No direct behavioral risk.

## Test Signals
`cargo check -p fuzzer-libfuzzer` should pass without generated bins.
