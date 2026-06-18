<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/internal/stats_export.go -->
# sources/user-network-fs/blobfuse2/tools/health-monitor/internal/stats_export.go

Source path: `sources/user-network-fs/blobfuse2/tools/health-monitor/internal/stats_export.go`

## Purpose
Part of the blobfuse2 health-monitor command, which samples process, blobfuse stats, and cache activity and exports JSON telemetry.

## Important APIs, Types, And Functions
Package functions: `NewStatsExporter`, `Destroy`, `AddMonitorStats`, `StatsExporter`, `addToList`, `checkInList`, `addToOutputFile`, `checkOutputFile`, `getNewFile`, `CloseExporter`. Types: `ExportedStat`, `StatsExporter`, `Output`. Imports: `encoding/json`, `fmt`, `os`, `path/filepath`, `sync`, `sync/atomic`, `github.com/Azure/azure-storage-fuse/v2/common`, `github.com/Azure/azure-storage-fuse/v2/common/log`, `github.com/Azure/azure-storage-fuse/v2/internal/stats_manager`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/common`.

## Control Flow
Creates a singleton exporter with a buffered channel and goroutine. Incoming timestamped stats are grouped into in-memory `Output` buckets, flushed to JSON arrays, and rotated once files reach the configured size/count limit.

## State And Persistence
Persists monitor JSON files under `OutputPath` named `monitor_<pid>.json` with numbered rotations. `pidStatus` prevents new channel writes during destroy, and `outputList` holds up to three recent timestamp buckets.

## Dependencies And Integration Points
Integrates with blobfuse2 health-monitor packages, shared `hmcommon` globals, monitor factory registration, named pipes, JSON/stat export files, and Azure Storage Fuse common logging/config packages.

## Risks
Type assertions depend on monitor names matching stat payload types. Dropping the oldest channel element on full buffer avoids blocking but can lose telemetry. JSON array formatting is hand-managed and vulnerable to abrupt process exit.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/internal/stats_export.go -->
