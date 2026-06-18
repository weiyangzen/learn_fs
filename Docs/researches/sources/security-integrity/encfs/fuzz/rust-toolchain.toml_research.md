## sources/security-integrity/encfs/fuzz/rust-toolchain.toml

Purpose: Rust toolchain pin for the fuzz subproject.

Important APIs and functions: `[toolchain] channel = "nightly"`. Control flow is rustup declarative selection when commands run inside `fuzz/`.

State and persistence: Causes rustup to install/select nightly if needed; no project runtime state. Dependencies are rustup and nightly compatibility with cargo-fuzz/libFuzzer. Integration matches Taskfile fuzz commands that explicitly use `cargo +nightly fuzz ...`. Risk: nightly drift can break fuzz builds; no date-pinned nightly is specified, so reproducibility is lower than the main package.
