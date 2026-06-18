<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-perf-site-replication.go -->
# sources/object-store/minio-mc/cmd/support-perf-site-replication.go

Purpose: runs site-replication network performance tests for `mc support perf site-replication`.

Important APIs/types/functions: `mainAdminSpeedTestSiteReplication` validates duration, calls `AdminClient.SiteReplicationPerf`, and converts `madmin.SiteNetPerfResult` into the support perf result model.

Control flow: after admin-client setup and positive duration validation, a goroutine invokes the admin API and sends one result or error. JSON mode prints the selected result/error directly. Interactive mode starts the shared speed-test UI and periodically sends empty site-replication result messages until completion, then forwards the final message to the UI and optional parent channel.

State and persistence: no direct local persistence. Results become part of the parent performance archive when run through `support perf`.

Dependencies and integration points: integrates with MinIO admin site-replication perf, shared `PerfTestResult` type constants, conversion helpers in `support-perf.go`, and Bubble Tea speed-test UI.

Risks and test signals: meaningful output requires a site-replication topology and server support. Tests should cover unsupported server errors, duration parsing, JSON conversion of per-node TX/RX durations and connection counts, and UI finalization.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-perf-site-replication.go -->
