# sources/storage-engines/tikv/fuzz/fuzzer-libfuzzer/template.rs

## Purpose
Template for generated libFuzzer harness binaries.

## Important APIs, Types, and Functions
Uses `#![no_main]`, imports `libfuzzer_sys`, aliases the selected `fuzz_targets` function, and defines `fuzz_target!(|data: &[u8]| { let _ = fuzz_target(data); })`.

## Control Flow
After placeholder substitution, libFuzzer owns process entry and repeatedly invokes the closure with mutated inputs from seed and corpus directories.

## State and Persistence Behavior
Template is static; generated harness files persist under `src/bin`. Runtime corpus evolution is handled by libFuzzer using CLI-provided directories.

## Dependencies and Integration Points
Depends on `libfuzzer-sys`, generated target names, and the `fuzz-targets` function signature.

## Risks
The ignored `Result` filters expected decode failures out of crash reporting. Invalid placeholder substitution creates compile-time errors rather than CLI-time errors.

## Test Signals
Generate a harness and run a short libFuzzer session with ASAN. Confirm crashes are reported for intentional panics in a temporary test target.
