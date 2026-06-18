<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/common/util.go -->
# sources/user-network-fs/blobfuse2/tools/health-monitor/common/util.go

Source path: `sources/user-network-fs/blobfuse2/tools/health-monitor/common/util.go`

## Purpose
Part of the blobfuse2 health-monitor command, which samples process, blobfuse stats, and cache activity and exports JSON telemetry.

## Important APIs, Types, And Functions
Package functions: `CheckProcessStatus`, `MonitorPid`. Types: none declared. Imports: `fmt`, `os/exec`, `strings`, `time`, `github.com/Azure/azure-storage-fuse/v2/common/log`.

## Control Flow
`CheckProcessStatus` shells out to `ps -ef | grep <pid>` and scans fields for the target pid; `MonitorPid` polls every second and allows monitor goroutines a short exit window after process loss.

## State And Persistence
No persisted state; it observes process tables and logs failures.

## Dependencies And Integration Points
Integrates with blobfuse2 health-monitor packages, shared `hmcommon` globals, monitor factory registration, named pipes, JSON/stat export files, and Azure Storage Fuse common logging/config packages.

## Risks
String-based `ps|grep` matching is platform-specific and may mis-detect edge cases; command invocation every second adds overhead.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/common/util.go -->
