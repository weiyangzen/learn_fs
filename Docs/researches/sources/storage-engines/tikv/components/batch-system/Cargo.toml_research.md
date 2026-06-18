# sources/storage-engines/tikv/components/batch-system/Cargo.toml

## Purpose
Defines the `batch-system` crate, a reusable TiKV component for batched finite-state-machine polling with mailbox routing, metrics, and optional test/benchmark support.

## APIs, Types, And Functions
The crate exposes a default `test-runner` feature that enables the `derive_more` dependency and test helper module. Main dependencies include `crossbeam`, `dashmap`, `resource_control`, `online_config`, prometheus metrics, TiKV utilities, and kvproto.

## Control Flow
Cargo metadata selects edition 2021 and enables the test runner by default. Test and benchmark targets are registered explicitly: `tests/cases/mod.rs`, `benches/router.rs`, and `benches/batch-system.rs`, all requiring the test runner where needed.

## State And Persistence
No runtime state exists in this manifest. It controls which crate modules and dev-only benchmark/test targets compile.

## Dependencies And Integration Points
The manifest reflects the component's integration points: resource controller scheduling, online config for batch sizing, prometheus for observability, and TiKV utilities for threading and channels.

## Risks And Test Signals
Feature coupling is the main risk: benchmarks and tests rely on `test-runner`; disabling default features changes available modules. The manifest provides explicit bench/test target definitions, which are strong signals that performance and routing behavior are first-class concerns.
