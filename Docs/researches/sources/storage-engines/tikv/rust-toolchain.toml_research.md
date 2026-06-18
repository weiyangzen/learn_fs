# sources/storage-engines/tikv/rust-toolchain.toml

## Purpose
Pins rustup-aware commands in the TiKV tree to `nightly-2026-01-30` with the minimal profile. This stabilizes compiler, formatter, clippy, source, and rust-analyzer behavior for development and CI.

## Important Settings and Control Flow
The `[toolchain]` table declares `channel = "nightly-2026-01-30"`, `components = ["rustfmt", "clippy", "rust-src", "rust-analyzer"]`, and `profile = "minimal"`. rustup reads this declaratively when Cargo, rustfmt, clippy, or editor tooling runs in the repository.

## State, Dependencies, Integration
Toolchain installation state lives in rustup, not the repo. The file integrates with `rustfmt.toml`, `scripts/clippy`, `scripts/test`, and frame-pointer or build-std paths in `scripts/run-cargo.sh`.

## Risks and Test Signals
The repository depends on an exact nightly and rustup availability. Toolchain bumps can alter compile, lint, and formatting behavior globally. Validate with `rustup show active-toolchain`, `cargo check`, `cargo clippy`, and `cargo fmt --check`.
