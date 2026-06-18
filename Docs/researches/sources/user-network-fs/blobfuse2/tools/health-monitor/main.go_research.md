<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/main.go -->
# sources/user-network-fs/blobfuse2/tools/health-monitor/main.go

Source path: `sources/user-network-fs/blobfuse2/tools/health-monitor/main.go`

## Purpose
Part of the blobfuse2 health-monitor command, which samples process, blobfuse stats, and cache activity and exports JSON telemetry.

## Important APIs, Types, And Functions
Package functions: `getMonitors`, `main`, `init`. Types: none declared. Imports: `flag`, `fmt`, `os`, `strings`, `time`, `github.com/Azure/azure-storage-fuse/v2/common`, `github.com/Azure/azure-storage-fuse/v2/common/log`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/common`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/internal`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/monitor`.

## Control Flow
Parses flags, initializes syslog logging, validates the target pid, suffixes blobfuse stats pipe names with pid, builds enabled monitors, launches each monitor goroutine, waits while the pid is alive, and closes the exporter.

## State And Persistence
Reads CLI flags into `hmcommon` globals, creates log files, named pipes, and JSON output files.

## Dependencies And Integration Points
Integrates with blobfuse2 health-monitor packages, shared `hmcommon` globals, monitor factory registration, named pipes, JSON/stat export files, and Azure Storage Fuse common logging/config packages.

## Risks
Monitor goroutines are launched without join/error propagation. Missing pid is fatal, but individual monitor failures are logged asynchronously.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/main.go -->
