# sources/storage-engines/raft-engine/ctl/Cargo.toml

## Purpose
Declares the `raft-engine-ctl` workspace package, a command-line control tool for inspecting and repairing raft-engine data.

## Important APIs, Types, And Functions
Package metadata sets version 0.4.2, edition 2018, Rust 1.75.0, and Apache-2.0 license. Dependencies are `clap` with derive/cargo features, `env_logger`, and the local `raft-engine` crate with `scripting` and `internals` features.

## Control Flow
Cargo builds this package as a workspace member. The `Makefile` target `ctl` builds it in release mode and copies the binary to `bin/`.

## State And Persistence Behavior
The manifest itself has no runtime state. Enabling `scripting` and `internals` gives the CLI access to unsafe repair and internal log queue APIs, which can mutate existing raft-engine data when invoked.

## Dependencies And Integration Points
Integrates with `ctl/src/lib.rs`, `ctl/src/main.rs`, Clap 3 command parsing, logger initialization, and root crate repair/check/dump APIs.

## Risks And Edge Cases
The CLI package advertises a lower Rust version than the root crate. The dependency version says `raft-engine` 0.4.1 while the local path package is 0.4.2, so publishing/versioning should be checked carefully.

## Test Signals
Build success through `make ctl` and any tests that invoke `run_command` or control APIs are the main signals.
