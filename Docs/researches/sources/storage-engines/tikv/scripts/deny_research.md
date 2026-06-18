# sources/storage-engines/tikv/scripts/deny

## Purpose
Installs and runs `cargo-deny` with a standalone Rust toolchain so dependency policy checks are decoupled from TiKV's primary build toolchain.

## Important Commands and Control Flow
The script pins `RUST_VERSION="1.92.0"`, installs it with rustup minimal profile, installs `cargo-deny@0.18.9` with `--locked`, prints `cargo deny -V`, runs `deny fetch all`, and then `deny check --show-stats`. The install command suppresses stderr and echoes a soft message on install failure, but later deny commands still enforce failure.

## State, Dependencies, Integration
It writes to rustup and Cargo install/cache locations, not normally to repository files. It depends on rustup, Cargo, network/cache availability, cargo-deny, and the repository deny configuration.

## Risks and Test Signals
The pinned Rust version and cargo-deny version must remain available. Suppressed install stderr can hide diagnostics. Network failures can prevent policy checks. Signals are successful `deny -V`, successful fetch, and zero exit from `deny check --show-stats`.
