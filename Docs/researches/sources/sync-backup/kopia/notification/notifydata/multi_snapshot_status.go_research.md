<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/multi_snapshot_status.go -->
# sources/sync-backup/kopia/notification/notifydata/multi_snapshot_status.go

- Purpose: Defines snapshot-result notification payloads and aggregate status helpers.
- Important APIs/types/functions: `ManifestWithError`, `StartTimestamp`, `EndTimestamp`, `TotalSize`, `TotalSizeDelta`, `TotalFiles`, `TotalFilesDelta`, `TotalDirs`, `TotalDirsDelta`, `Duration`, status constants, `StatusCode`, `MultiSnapshotStatus`, `EventArgsType`, `OverallStatusCode`, `OverallStatus`.
- Control flow: Per-manifest methods derive metrics from root entries and optional previous snapshots. Status codes prioritize top-level error, incomplete reason, fatal summary errors, ignored errors, then success. Aggregate status reports fatal/warning/success and user-facing text.
- State and persistence: JSON event payload embeds snapshot manifests; persistence is notification transport/template rendering only.
- Dependencies and integration points: Integrates `grpcapi`, `fs`, and `snapshot`; consumed by snapshot notification templates.
- Risks and edge cases: Overall status code intentionally ignores incomplete as fatal/warning; delta methods return fallback values when summaries are missing.
- Test signals: `multi_snapshot_status_test.go` covers status text/codes, metrics, deltas, duration, and round trip.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/multi_snapshot_status.go -->
