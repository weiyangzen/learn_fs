# sources/storage-engines/tikv/fuzz/cli.rs

## Purpose
Implements a command-line driver for TiKV fuzz targets. It lists discovered targets and runs a selected target through AFL, Honggfuzz, or libFuzzer by generating fuzzer-specific binary source files from templates.

## Important APIs, Types, and Functions
Lazy globals compute `WORKSPACE_ROOT`, `FUZZ_ROOT`, `FUZZ_TARGETS`, and `SEED_ROOT`. `Cli` supports `list-targets` and `run`. `Fuzzer` maps to package names and directories. `write_fuzz_target_source_file`, `run`, `get_seed_dir`, `create_corpus_dir`, `pre_check`, `run_afl`, `run_honggfuzz`, and `run_libfuzzer` implement generation and execution.

## Control Flow
Target discovery reads `fuzz/targets/mod.rs` and extracts `pub fn fuzz_(\w+)(` names. `run` validates the target, writes `src/bin/<target>.rs` for the chosen fuzzer, then dispatches. AFL builds an instrumented binary and invokes `cargo afl fuzz`; Honggfuzz sets sanitizer flags and `HFUZZ_RUN_ARGS`; libFuzzer sets sanitizer coverage flags, target triple, ASAN options, corpus dir, and seed dir.

## State and Persistence Behavior
Creates or overwrites generated fuzzer binary files and corpus directories under fuzzer package directories. Reads seed directories, falling back to `common/seeds/default`. It also relies on and mutates process environment passed to child `cargo` commands.

## Dependencies and Integration Points
Depends on `anyhow`, `structopt`, `cargo_metadata`, `regex`, `lazy_static`, and external cargo subcommands `cargo afl` or `cargo hfuzz`. Integrates with fuzzer templates and the `fuzz-targets` library.

## Risks
`pre_check` unwraps command status, so a missing executable can panic instead of returning context. Regex discovery can miss valid targets or match unintended public functions if signature style changes. Generated source is written into the tree and may become stale. Sanitizer flags require nightly/toolchain/platform support.

## Test Signals
Run `list-targets`, validate generated source for each fuzzer, and perform dry-run/pre-check tests with missing and installed fuzzer tools. Add tests for target regex discovery and seed fallback behavior.
