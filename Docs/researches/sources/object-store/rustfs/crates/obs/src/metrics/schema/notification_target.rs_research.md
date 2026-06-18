# sources/object-store/rustfs/crates/obs/src/metrics/schema/notification_target.rs

## Purpose
Defines per-notification-target queue, success, and permanent failure descriptors.

## Important APIs, Types, and Functions
Exports label constants `TARGET_ID` and `TARGET_TYPE`, a private two-label array, and three `LazyLock<MetricDescriptor>` descriptors: failed messages counter, queue length gauge, and total messages counter. All use `subsystems::NOTIFICATION`.

## Control Flow
Lazy descriptor construction only.

## State and Persistence
No values or persistence. The notification target collector supplies per-target values and labels.

## Dependencies and Integration Points
Used by notification target collector code and shares the `notification` subsystem with aggregate notification descriptors. Label constants provide a stable contract for target dimensions.

## Risks
High-cardinality `target_id` values can affect Prometheus cardinality if many targets exist or IDs are unstable. Collectors must always provide both labels in the declared order.

## Test Signals
No direct tests. Collector tests should assert label presence and full metric names.
