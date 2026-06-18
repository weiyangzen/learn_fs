# sources/object-store/rustfs/crates/obs/src/metrics/schema/entry/subsystem.rs

## Purpose
Defines metric subsystems, their canonical URL-like paths, and convenience constants used by descriptor modules.

## Important APIs, Types, and Functions
`MetricSubsystem` enumerates API, bucket, system, debug, cluster, ILM, audit, replication, notification, scanner, and `Custom(String)` subsystems. `path()` returns canonical path strings, `as_str()` normalizes paths into metric-name segments, `from_path()` parses known paths, `new()` creates custom paths, and `Display` writes the path. The nested `subsystems` module exposes constants such as `API_REQUESTS`, `SYSTEM_DRIVE`, and `CLUSTER_IAM`.

## Control Flow
`path()` and `from_path()` are large matches over known paths. Unknown paths become `Custom`. Full metric-name generation calls `as_str()`, which uses `format_path_to_metric_name()`.

## State and Persistence
No runtime values. Custom subsystem variants store a path string inside descriptors.

## Dependencies and Integration Points
Every schema file depends on these subsystem constants. Collectors and dashboards depend on the normalized path names, for example `/system/network/internode` becomes `system_network_internode`.

## Risks
New schema modules must add both enum variants and constants or use `Custom`, which may reduce consistency. Unknown paths are silently accepted as custom, so path typos can create new metric families instead of failing. The `CLUSTER_BASE_PATH` constant is present but not central to descriptor construction.

## Test Signals
Tests validate formatting for common and custom paths and full descriptor name generation with built-in and custom subsystems.
