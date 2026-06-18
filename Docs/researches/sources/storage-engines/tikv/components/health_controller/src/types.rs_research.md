# sources/storage-engines/tikv/components/health_controller/src/types.rs

Purpose: shared latency-inspection data structures for health-controller reporters.

Important APIs/types/functions: `RaftstoreDuration` with store/apply stage durations; `sum`, `delays_on_disk_io`, `delays_on_net_io`; `InspectFactor`; `LatencyInspector`.

Control flow: instrumentation records optional stage durations into a `LatencyInspector`; `finish` consumes it and invokes the callback with ID and duration. Reporters classify collected durations as disk or network delay.

State and persistence: transient in-memory per inspection; missing fields default to zero when summarized.

Dependencies/integration: exported from `lib.rs` and consumed by raftstore health reporting.

Risks: incomplete instrumentation underreports because missing durations are zero; `InspectFactor` discriminants are used as vector indices.

Test signals: no direct tests; covered indirectly by reporter behavior.
