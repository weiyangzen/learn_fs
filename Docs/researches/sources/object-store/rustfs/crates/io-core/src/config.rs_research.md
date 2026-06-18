# sources/object-store/rustfs/crates/io-core/src/config.rs

Purpose: central configuration types for scheduler and priority queue behavior.

Important APIs/types: `IoSchedulerConfig` covers concurrent read limits, size-based priority thresholds, per-priority queue capacities, starvation/load timing, feature flags for detection/monitoring/adaptive buffering, and base/min/max buffer sizes. `ConfigError` reports invalid values. `IoPriorityQueueConfig` is a smaller queue-specific projection with capacities and starvation durations.

Control flow: defaults set conservative capacities and enable priority scheduling, storage/sequential detection, bandwidth monitoring, and adaptive buffers. `validate` enforces positive concurrency, high priority size threshold lower than low threshold, and coherent buffer min/base/max. Builder helpers mutate selected groups of fields. Duration helpers convert millisecond/second scalar fields to `Duration`. `IoPriorityQueueConfig::from_scheduler_config` adapts scheduler config into queue config.

State and persistence: plain cloneable structs only; no runtime state or persistence.

Dependencies and integration: standard `Duration` and `thiserror`; consumed by `io_priority_queue`, `scheduler`, examples, and public re-exports.

Risks: validation does not check queue capacities, load sample window, waterline semantics, or zero buffer sizes beyond min/base/max relationships. Builder helpers do not validate immediately, so callers must remember to call `validate`.

Test signals: tests cover default validity, invalid concurrency/threshold/buffer configurations, builder mutation, queue config conversion, and duration helpers.
