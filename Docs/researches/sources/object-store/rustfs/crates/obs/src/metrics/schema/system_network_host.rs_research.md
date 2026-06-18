# sources/object-store/rustfs/crates/obs/src/metrics/schema/system_network_host.rs

## Purpose
Defines host-wide network I/O descriptors for aggregate and per-interface byte transfer metrics.

## Important APIs, Types, and Functions
Exports `HOST_NETWORK_IO_MD` and `HOST_NETWORK_IO_PER_INTERFACE_MD`, both no-label gauges under `subsystems::SYSTEM_NETWORK_HOST`.

## Control Flow
Lazy descriptor construction only.

## State and Persistence
No values. `collect_host_network_stats()` uses `sysinfo::Networks::new_with_refreshed_list()` to collect total received/transmitted bytes and per-interface tuples.

## Dependencies and Integration Points
Used by `metrics/collectors/system_network_host.rs`, which adds direction/interface labels at emission time even though this schema declares no labels.

## Risks
The descriptors currently declare empty label sets, but the collector appears to distinguish received/transmitted and per-interface values through labels. That mismatch should be tested because descriptor label metadata may not reflect emitted metric cardinality. Host counters are not process-specific.

## Test Signals
No schema tests. Collector tests should specifically validate label metadata and emitted label sets for aggregate versus per-interface metrics.
