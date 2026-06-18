# sources/storage-engines/tikv/fuzz/fuzzer-afl/template.rs

## Purpose
Template for generated AFL binary harnesses.

## Important APIs, Types, and Functions
Imports the AFL macro crate and `fuzz_targets`, aliases the selected target via `use fuzz_targets::__FUZZ_CLI_TARGET__ as fuzz_target`, and defines `main` with `fuzz!(|data: &[u8]| { let _ = fuzz_target(data); })`.

## Control Flow
The CLI replaces `__FUZZ_CLI_TARGET__` and the generated-comment token, writes the resulting file under `src/bin`, and AFL repeatedly invokes the closure with mutated byte slices.

## State and Persistence Behavior
The template is static; generated files are persisted in the fuzzer package until overwritten. Runtime corpus/crash state is owned by AFL output directories.

## Dependencies and Integration Points
Requires AFL macro support, `fuzz-targets`, and the CLI replacement contract. It must match the target function signature `fn(&[u8]) -> Result<()>`.

## Risks
The target result is ignored, so ordinary parse errors do not fail the fuzz case; only panics/abort/sanitizer issues are findings. Template placeholders are string-replaced without syntax validation until compile time.

## Test Signals
Generate a known target and run `cargo afl build --bin <target>`. Confirm malformed target names are rejected before template generation.
