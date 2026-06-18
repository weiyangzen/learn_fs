<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/blobfuse_stats/stats_reader.go -->
# sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/blobfuse_stats/stats_reader.go

Source path: `sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/blobfuse_stats/stats_reader.go`

## Purpose
Part of the blobfuse2 health-monitor command, which samples process, blobfuse stats, and cache activity and exports JSON telemetry.

## Important APIs, Types, And Functions
Package functions: `GetName`, `SetName`, `Monitor`, `ExportStats`, `Validate`, `statsReader`, `statsPoll`, `createPipe`, `NewBlobfuseStatsMonitor`, `init`. Types: `BlobfuseStats`. Imports: `bufio`, `encoding/json`, `fmt`, `os`, `syscall`, `time`, `github.com/Azure/azure-storage-fuse/v2/common`, `github.com/Azure/azure-storage-fuse/v2/common/log`, `github.com/Azure/azure-storage-fuse/v2/internal/stats_manager`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/common`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/internal`.

## Control Flow
Validates polling interval and pid, creates transfer and polling named pipes, reads newline-delimited JSON `stats_manager.PipeMsg` records from the transfer pipe, and periodically writes poll messages to the polling pipe.

## State And Persistence
Creates FIFO files using blobfuse common pipe names with pid suffixes and streams stats into the shared exporter.

## Dependencies And Integration Points
Integrates with blobfuse2 health-monitor packages, shared `hmcommon` globals, monitor factory registration, named pipes, JSON/stat export files, and Azure Storage Fuse common logging/config packages.

## Risks
Named pipe open/read behavior can block or fail if the blobfuse process does not cooperate. Malformed JSON records are skipped after logging.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/blobfuse_stats/stats_reader.go -->
