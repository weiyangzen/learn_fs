# sources/object-store/minio/cmd/metrics-realtime.go

Purpose: This file collects on-demand local and remote realtime metrics for disks, scanner, OS, batch jobs, site resync, network, memory, CPU, and RPC subsystems.

Important APIs and types: `collectMetricsOpts` filters hosts, disks, job ID, and deployment ID. `collectLocalMetrics` returns `madmin.RealtimeMetrics`; `collectLocalDisksMetrics` returns per-disk `madmin.DiskMetric`; `collectRemoteMetrics` merges peer metrics from the notification system.

Control flow: `collectLocalMetrics` exits for `MetricsNone`, resolves the reporting host name, and conditionally fills requested metric groups based on `madmin.MetricType.Contains`. Disk collection builds per-disk metrics and an aggregate. Scanner, OS, batch, and site-resync metrics come from global metric reporters. Network stats query the internode interface. Memory uses `madmin.GetMemInfo`. CPU uses gopsutil CPU time/count/load calls. RPC reads grid connection stats if the grid is initialized. The final metrics object stores a shallow `ByHost` map pointing at the aggregate. Remote collection is skipped unless the node is distributed erasure, then all peer responses are merged.

State and persistence behavior: The file does not persist data. It samples global runtime state and OS counters. Disk metrics include lifetime and last-minute API calls, healing/offline markers, and Linux drive stats when available.

Dependencies and integration points: It integrates with madmin metric types, global scanner/OS/batch/site-resync metric providers, object-layer storage info, internal disk and net packages, gopsutil CPU/load, global grid stats, endpoint host resolution, and the notification system's peer metric fan-out.

Risks: Host filtering depends on endpoint naming and can return an empty result for mismatches. OS/stat calls can fail and are recorded as strings in `Errors`. `ByHost` uses a shallow aggregate reference, so callers must avoid mutating shared data. Disk stat availability varies by platform and drive state. Remote merge behavior depends on peer responsiveness and distributed-erasure mode.

Test signals: No direct tests are present in this subset. Signals should come from admin/metrics integration tests that assert selected metric groups appear, errors are surfaced, host/disk filtering works, and distributed peer merges preserve local plus remote values.
