# sources/storage-engines/tikv/components/engine_panic/src/flow_control_factors.rs

Purpose: Panic skeleton for engine flow-control metrics.

Important APIs and types: `PanicEngine` implements `FlowControlFactorsExt` methods for number of files at level, immutable memtable count, and pending compaction bytes.

Control flow and state: All methods panic and return no values.

Dependencies and integration: Real engines use these metrics for write-flow control decisions; this file keeps the skeleton API-complete.

Risks: Runtime calls panic.

Test signals: No tests.
