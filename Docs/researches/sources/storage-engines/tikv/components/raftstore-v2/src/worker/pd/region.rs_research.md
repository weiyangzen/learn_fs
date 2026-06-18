# sources/storage-engines/tikv/components/raftstore-v2/src/worker/pd/region.rs

Purpose: this file implements PD worker region-level heartbeat/stat handling, bucket reporting, CPU record accounting, and PD heartbeat response dispatch.

Important APIs/types/functions: `RegionHeartbeatTask` carries leader heartbeat data. `PeerStat` stores accumulated read/query/write snapshot baselines and approximate size/key data. `ReportBucket` tracks current and last-reported bucket stats and computes deltas. Runner methods include `handle_region_heartbeat`, `maybe_schedule_heartbeat_receiver`, `handle_report_region_buckets`, read/write stats updates, CPU record handling, `handle_destroy_peer`, `merge_buckets`, and `calculate_region_cpu_records`.

Control flow: region heartbeat converts approximate size 0 to 1 for compatibility, computes deltas since last region report, consumes region CPU records, builds `RegionStat`, updates store histograms, and sends async PD heartbeat. The heartbeat response receiver is installed once and translates PD operators into admin requests or peer messages: change peer, change peer v2, transfer leader, split by keys/half split, merge, or noop. Read/write stats accumulate per-region counters and feed `PdStatsMonitor`; bucket reports merge deltas then report PD deltas over elapsed seconds.

State and persistence: all stats maps are in memory: `region_peers`, `region_buckets`, and CPU records split by region-heartbeat and store-heartbeat windows. Destroy-peer removes stale stat records. Persistent changes from PD responses happen only after routed raft admin proposals apply.

Dependencies/integration: depends on PD client heartbeat APIs, `PdStatsMonitor`, resource metering raw records, router messages, admin request helper constructors, and request split/half-split operation types.

Risks: delta accounting assumes monotonic counters; resets can underflow because subtraction is direct. Heartbeat receiver panics on unexpected PD stream error. Bucket metadata changes require merge recalculation to align old stats to current bucket layout.

Test signals: local test `test_remove_peer_stat_from_maps` verifies destroy cleanup removes peer and CPU stats. Broader behavior needs PD heartbeat integration tests.
