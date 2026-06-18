# sources/storage-engines/tikv/components/raftstore-v2/src/worker/pd/slowness.rs

Purpose: this file implements store slowness trend detection and reporting for raftstore-v2 PD store stats.

Important APIs/types/functions: `SlownessStatistics` contains a cause `Trend`, result `Trend`, QPS recorder, and `last_tick_finished` flag. Runner methods include `handle_update_slowness_stats`, `handle_graceful_shutdown_state`, `handle_slowness_stats_tick`, `update_slowness_in_store_stats`, and private `flush_slowness_metrics`.

Control flow: periodic stats monitor creates latency inspectors; completed inspections call `handle_update_slowness_stats`, marking the tick finished and recording total raftstore duration as cause signal. On slowness tick, an unfinished previous tick records a large interval and may trigger a fake store heartbeat if real heartbeat is delayed; otherwise it records 100ms white noise. Store stats update computes slow trend cause/result values and rates, records QPS into result trend, sets PD protobuf `SlowTrend`, and flushes Prometheus gauges.

State and persistence: slowness state is in memory and exported through metrics and store heartbeat PD stats. Graceful shutdown state is stored in an atomic and triggers a store heartbeat tick message.

Dependencies/integration: depends on health-controller trend types, raftstore metrics, store heartbeat interval, PD store stats protobufs, and router control messages.

Risks: trend thresholds are heuristic and comments note compatibility-driven simplification of disk/network causes. If inspector ticks hang, fake heartbeat behavior prevents PD from missing slow state but can report synthetic data. Failpoint can force unfinished tick behavior.

Test signals: no local tests. Failpoint `mock_slowness_last_tick_unfinished` supports behavior testing.
