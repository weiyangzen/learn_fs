# sources/object-store/rustfs/crates/ecstore/run_benchmarks.sh

Purpose: Bash helper for running ecstore Reed-Solomon SIMD benchmark modes and producing Criterion reports.

Important functions: colorized logging helpers, `check_requirements`, `cleanup`, mode runners for `simd`, `full`, `performance`, `large`, `quick`, `generate_comparison_report`, `show_help`, `show_test_info`, and `main`.

Control flow: `main` checks Cargo availability, prints Rust/Cargo/CPU/SIMD environment details, dispatches on the first argument, optionally removes `target/criterion`, runs `cargo bench` with selected bench names and filters, then reports where HTML output lives.

State and persistence: deletes previous Criterion results with `rm -rf target/criterion` for most full modes, then `cargo bench` recreates benchmark artifacts under `target/criterion`.

Dependencies and integration points: assumes Bash, Cargo, Rust toolchain, optional `/proc/cpuinfo` on Linux, optional Python 3 for serving generated reports. It calls `comparison_benchmark` and `erasure_benchmark` declared in `Cargo.toml`.

Risks: `set -e` stops on first failing command. The `cargo --list | grep bench` check is a weak proxy for Criterion support. `--quick` is passed through to Criterion filters/options and should be verified against the installed Criterion version.

Test signals: operational benchmark runner rather than correctness test; useful for repeatable local performance baselines.
