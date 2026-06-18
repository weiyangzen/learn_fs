# sources/storage-engines/raft-engine/stress/Cargo.toml

Purpose: this manifest defines the standalone `stress` binary crate for exercising raft-engine under configurable read/write/purge workloads.

Important APIs and types: as a Cargo manifest, it declares package metadata (`name = "stress"`, version `0.4.2`, Rust 2018) and dependencies. The most important dependency is `raft-engine = { path = "..", features = ["internals"] }`, which gives the stress binary access to engine internals and event listener hooks.

Control flow: Cargo uses this manifest to build the stress tool independently from the main crate. The dependency set enables command-line parsing (`clap` derive/cargo), constant formatting for default CLI strings, latency histograms, raft protobuf entries, spin-wait timing, randomness, distributions, and summary statistics.

State and persistence behavior: no runtime state is stored here. The dependency on `raft` from the master branch of `tikv/raft-rs` is a build-time external source, and the path dependency ties the stress crate directly to the checked-out raft-engine implementation.

Dependencies and integration points: dependencies are `clap`, `const_format`, `hdrhistogram`, `num-traits`, `parking_lot_core`, git `raft`, path `raft-engine` with internals, `rand`, `rand_distr`, and `statistical`. These map directly to the parser, version conversion, spin wait, entry generation, event hooks, workload randomness, and reporting in `stress/src/main.rs`.

Risks and invariants: the git dependency on raft master can make builds non-reproducible unless Cargo.lock pins it. The `internals` feature means the binary can rely on non-public engine APIs. This manifest is for tooling/stress validation, not a library consumed by production.

Test signals: no tests in the manifest. Successful build of the stress crate is the main signal that its dependency graph remains compatible.
