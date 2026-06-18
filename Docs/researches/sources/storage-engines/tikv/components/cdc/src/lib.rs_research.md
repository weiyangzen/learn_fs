# sources/storage-engines/tikv/components/cdc/src/lib.rs

## Purpose

`lib.rs` is the crate root for TiKV's CDC component. It declares the internal CDC modules and re-exports the public API surface used by the rest of TiKV: event/channel primitives, configuration manager, delegate and endpoint types, error/result types, observer, old-value cache, and service entry points.

## Important APIs, Types, And Functions

- Enables `#![feature(box_patterns)]`, which is required by `errors.rs` nested error matching.
- Declares internal modules: `channel`, `config`, `delegate`, `endpoint`, `errors`, `initializer`, `observer`, `old_value`, `service`, `txn_source`, `types`, and `watchdog`.
- Exposes `metrics` as a public module.
- Re-exports:
  - `channel::{CdcEvent, recv_timeout}`
  - `config::CdcConfigManager`
  - `delegate::Delegate`
  - `endpoint::{CdcTxnExtraScheduler, Endpoint, Task, Validate}`
  - `errors::{Error, Result}`
  - `observer::CdcObserver`
  - `old_value::OldValueCache`
  - `service::{FeatureGate, Service}`

## Control Flow

There is no runtime control flow in this file. Its role is module wiring and public export selection. The larger CDC control flow starts from `Service` and `CdcObserver`, schedules `Task` values into `Endpoint`, uses `Initializer` for incremental scan, and delegates per-region event conversion to `Delegate`.

## State And Persistence Behavior

`lib.rs` has no state or persistence behavior. It controls crate visibility.

## Dependencies And Integration Points

The file integrates this crate with external TiKV components by exposing only selected types. `Endpoint`, `Task`, and `CdcTxnExtraScheduler` are required by worker/router wiring; `CdcObserver` integrates with raftstore coprocessor observation; `Service` is the gRPC-facing CDC service; `OldValueCache` and `metrics` support monitoring and old-value paths.

## Risks And Edge Cases

- Export changes can become crate API changes for other TiKV modules.
- The crate relies on nightly `box_patterns`; removing or stabilizing nested error matching would require coordinated updates in `errors.rs`.
- Making modules public accidentally would widen the maintenance surface; currently most internals remain private.

## Test Signals

There are no direct tests for `lib.rs`. Compile tests and downstream module tests validate that the module graph and re-exports are correct.
