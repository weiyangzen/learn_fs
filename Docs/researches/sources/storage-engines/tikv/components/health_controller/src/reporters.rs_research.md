# sources/storage-engines/tikv/components/health_controller/src/reporters.rs

Purpose: converts raftstore latency observations into health-controller slow scores, slow-trend protobufs, network scores, and module unhealthy markers.

Important APIs/types/functions: `RaftstoreReporterConfig`, `UnifiedSlowScore`, `RaftstoreReporter`, `SlowTrendStatistics`, and `TestReporter`. Main methods record disk/network durations, tick factors, get disk/network scores, update slow trend, and publish health-controller state.

Control flow: disk records update trend cause, per-factor disk score, and aggregate max disk score. Network records pull latencies from the controller and maintain one `SlowScore` per store. Disk ticks handle unfinished inspections, recover health on completed ticks, and mark raftstore unhealthy when score rounds lack new records. Network ticks synchronize per-store tick IDs and average only complete updates.

State and persistence: all state is in memory; disk scores are local, network scores are behind `Arc<Mutex<HashMap<...>>>`, and published values go to `HealthControllerInner`.

Dependencies/integration: depends on `slow_score`, `trend`, `types::InspectFactor`, `kvproto::pdpb::SlowTrend`, and Prometheus gauges. The PD worker is expected to drive ticking.

Risks: tick-ID drift would corrupt network attribution; poisoned network mutex panics; no-record disk rounds mark health unknown/unhealthy.

Test signals: tests cover network factor lifecycle, tick synchronization, timeout growth, and recovery.
