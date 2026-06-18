# sources/storage-engines/tikv/fuzz/fuzzer-honggfuzz/template.rs

## Purpose
Template for generated Honggfuzz binary harnesses.

## Important APIs, Types, and Functions
Imports the Honggfuzz macro crate and `fuzz_targets`, aliases the selected target, and runs an infinite loop invoking `fuzz!(|data| { let _ = fuzz_target(data); })`.

## Control Flow
The CLI substitutes the target name and generated comment. At runtime Honggfuzz controls input generation and the loop keeps requesting new inputs until crash, stop, or timeout.

## State and Persistence Behavior
Template is static; generated binary source persists under the fuzzer crate. Corpus and crash artifacts are managed by Honggfuzz.

## Dependencies and Integration Points
Requires the target function to be exported from `fuzz-targets` and the `honggfuzz` macro to be available on the host.

## Risks
Ignoring `Result` means expected parsing failures are not treated as crashes. Infinite loop behavior is correct for Honggfuzz but should not be copied to one-shot harnesses.

## Test Signals
Generate and compile a target with `cargo hfuzz run <target>` in a short run. Confirm sanitizer flags supplied by the CLI work with the local nightly compiler.
