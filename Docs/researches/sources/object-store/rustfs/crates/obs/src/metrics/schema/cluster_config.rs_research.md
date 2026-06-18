# sources/object-store/rustfs/crates/obs/src/metrics/schema/cluster_config.rs

Purpose: defines metric descriptors for cluster storage-class parity configuration.

Important APIs/types: `CONFIG_RRS_PARITY_MD` and `CONFIG_STANDARD_PARITY_MD`, both gauges with no labels under `subsystems::CLUSTER_CONFIG`.

Control flow: lazy descriptor construction through `new_gauge_md` and `MetricName::ConfigRRSParity` / `MetricName::ConfigStandardParity`.

State/persistence: lazy immutable descriptors only.

Dependencies/integration: consumed by `collectors/cluster_config.rs`, conditionally emitted by the scheduler's supplementary cluster task when config stats are available.

Risks: configuration metrics are gauges but represent static/effective config; if config reloads are supported, upstream must refresh values. Absence should be modeled by not emitting rather than emitting default zero.

Test signals: collector tests validate output count and values for both parity descriptors.
