<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/network_profiler/network_monitor.go -->
# sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/network_profiler/network_monitor.go

Source path: `sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/network_profiler/network_monitor.go`

## Purpose
Part of the blobfuse2 health-monitor command, which samples process, blobfuse stats, and cache activity and exports JSON telemetry.

## Important APIs, Types, And Functions
Package functions: `GetName`, `SetName`, `Monitor`, `ExportStats`, `Validate`, `NewNetworkMonitor`, `init`. Types: `NetworkProfiler`. Imports: `fmt`, `github.com/Azure/azure-storage-fuse/v2/common/log`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/common`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/internal`.

## Control Flow
Defines a monitor shell with validation and exporter plumbing, but its `init` registration is commented out and `Monitor` returns after validation.

## State And Persistence
No network stats are collected or persisted.

## Dependencies And Integration Points
Integrates with blobfuse2 health-monitor packages, shared `hmcommon` globals, monitor factory registration, named pipes, JSON/stat export files, and Azure Storage Fuse common logging/config packages.

## Risks
The monitor is present in constants and disable flags but inactive; users may assume network telemetry exists when it does not.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/network_profiler/network_monitor.go -->
