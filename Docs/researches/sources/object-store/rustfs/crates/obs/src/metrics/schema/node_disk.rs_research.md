# sources/object-store/rustfs/crates/obs/src/metrics/schema/node_disk.rs

## Purpose
Defines node-scoped disk capacity descriptors for total, used, and free bytes.

## Important APIs, Types, and Functions
Exports private labels `SERVER_LABEL` and `DRIVE_LABEL`, and three `LazyLock<MetricDescriptor>` descriptors using `MetricName::Custom("disk_*_bytes")` and `MetricSubsystem::new("/node")`.

## Control Flow
Only lazy initialization. The custom subsystem `/node` normalizes to the metric segment `node`.

## State and Persistence
No metric values or persistence. Values are populated by `collect_disk_stats()` via storage admin `storage_info`.

## Dependencies and Integration Points
Used by `metrics/collectors/node.rs`, which attaches `server` and `drive` labels. This schema is distinct from `system_drive.rs`, which exports richer drive metrics under `/system/drive`.

## Risks
The custom `/node` subsystem is not a built-in enum variant, so typos would be unchecked. Label ordering must match collector code. There is overlapping disk capacity visibility with `system_drive.rs`.

## Test Signals
Collector tests check generated names for node disk metrics. There are no local schema tests.
