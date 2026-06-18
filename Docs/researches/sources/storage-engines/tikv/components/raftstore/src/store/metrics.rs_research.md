# `sources/storage-engines/tikv/components/raftstore/src/store/metrics.rs`

## Purpose
This file is the central Prometheus metric registry for raftstore store, peer, apply, snapshot, compaction, split, hibernation, write, IO, and slow-store observability. It defines static metric label enums and registers the global counters, gauges, histogram vectors, and local-auto-flush wrappers consumed by raftstore runtime code.

## Important APIs, Types, and Functions
- `make_auto_flush_static_metric!` declares label enums and typed local wrappers for perf context, write/admin commands, snapshot validation, region hash, CF names, raft entry fetches, warmup, snapshot CF metrics, and compaction guard actions.
- `make_static_metric!` declares typed vectors for raft ready, sent/dropped messages, proposals, invalid proposals, store event durations, raft log GC skip reasons, load-based split events, snapshot BR events, hibernated state, busy-on-apply gauges, CPU pool gauges, and snapshot generate-byte counters.
- `lazy_static!` registers global Prometheus metrics such as `STORE_TIME_HISTOGRAM`, `APPLY_TIME_HISTOGRAM`, store write histograms, waterfall histograms, IO duration histograms, proposal/admin/write counters, snapshot metrics, raft ready/message counters, read-index metrics, load split metrics, entry-cache metrics, slow trend gauges, snapshot BR metrics, and busy/CPU gauges.

## Control Flow
There is no runtime algorithm beyond lazy registration. Consumers import typed metrics or raw Prometheus handles, create local handles when needed, increment/observe on hot paths, and flush via local metrics code. The static metric macros provide compile-time field names for label combinations, which reduces label typo risk and keeps call sites ergonomic.

## State and Persistence Behavior
All state is Prometheus process memory. No raftstore data is persisted. Metric cardinality is mostly bounded by static labels, except a few vector labels such as store id, output level, target, type/window strings, and read-QPS order.

## Dependencies and Integration Points
The file depends on `lazy_static`, `prometheus`, and `prometheus_static_metric`. It is imported by `local_metrics.rs`, store/peer/apply/snapshot/worker modules, and re-exported in part by `store/mod.rs` (`RAFT_ENTRY_FETCHES_VEC`). Metric labels must remain aligned with `StoreTick::tag`, `PeerTick` handling, raft message mappings, proposal classification, snapshot validation, and worker code.

## Risks and Edge Cases
- Metric registration uses `unwrap`; duplicate metric names or incompatible label sets will panic during lazy initialization.
- Changing static label enums can break call sites and dashboards.
- High-cardinality dynamic labels must be treated carefully; `MESSAGE_RECV_BY_STORE` labels by store id and can grow with cluster membership.
- Local metrics can hide recent events until flushed by `local_metrics.rs`.
- Histogram bucket choices encode operational assumptions; changing them impacts alerting and dashboard comparability.

## Test Signals
There are no local tests. Compilation is the main guard for static metric field names. Runtime test signals should include metric registration smoke tests, dashboard/alert compatibility checks, and code review for new labels or metric names.
