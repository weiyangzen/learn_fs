# sources/storage-engines/tikv/src/storage/txn/flow_controller/mod.rs

## Purpose
`flow_controller/mod.rs` is the facade for transaction scheduler flow control. It exposes a single `FlowController` enum over the singleton engine-wide controller and the per-tablet controller, allowing the rest of storage code to call one API regardless of engine deployment mode.

## Important APIs, types, and functions
The module publicly re-exports `EngineFlowController` and `TabletFlowController`, declares submodules, and defines `FlowController::{Singleton, Tablet}`. It forwards `should_drop`, `consume`, `unconsume`, `is_unlimited`, `update_config`, `enable`, and `enabled`; tests also get `discard_ratio`, `total_bytes_consumed`, and `set_speed_limit`. The `flow_controller_fn!` macro reduces forwarding boilerplate.

## Control flow
All methods simply match on the enum variant and delegate to the underlying implementation. `consume(region_id, bytes)` returns a delay duration from the relevant limiter. `should_drop(region_id)` performs probabilistic admission control in the underlying controller. `update_config` mutates the shared online config tracker owned by the concrete controller.

## State and persistence behavior
This module owns no state beyond the enum variant. All mutable runtime state lives in `singleton_flow_controller.rs` or `tablet_flow_controller.rs`: limiters, discard ratios, background checker threads, config trackers, and per-region maps. No persistent storage is touched here.

## Dependencies and integration points
It depends on `online_config::ConfigChange` and `Duration`, and integrates transaction scheduler callers with both flow-control backends. The facade lets scheduler code remain independent of whether TiKV is using one RocksDB instance or tabletized per-region engines.

## Risks
The main risk is API drift between the singleton and tablet controllers. Because forwarding is manual or macro-generated, any new method must be implemented consistently in both concrete controllers and forwarded here. Region ID semantics also differ by backend: singleton ignores region ID, while tablet mode depends on it.

## Test signals
This file has no local tests, but the concrete controller tests exercise the facade by wrapping controllers in `FlowController` and calling common helper functions. That provides indirect coverage for forwarding correctness.
