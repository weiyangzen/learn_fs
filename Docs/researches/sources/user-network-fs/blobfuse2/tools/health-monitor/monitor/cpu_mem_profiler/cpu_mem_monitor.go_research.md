<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/cpu_mem_profiler/cpu_mem_monitor.go -->
# sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/cpu_mem_profiler/cpu_mem_monitor.go

Source path: `sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/cpu_mem_profiler/cpu_mem_monitor.go`

## Purpose
Part of the blobfuse2 health-monitor command, which samples process, blobfuse stats, and cache activity and exports JSON telemetry.

## Important APIs, Types, And Functions
Package functions: `GetName`, `SetName`, `Monitor`, `ExportStats`, `Validate`, `getCpuMemoryUsage`, `getCpuMemIndex`, `NewCpuMemoryMonitor`, `init`. Types: `CpuMemProfiler`. Imports: `fmt`, `math`, `os/exec`, `strings`, `time`, `github.com/Azure/azure-storage-fuse/v2/common/log`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/common`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/internal`.

## Control Flow
On each process-monitor tick, executes `top`, parses header positions for `%CPU` and `VIRT`, normalizes units, then exports CPU and/or memory values depending on disabled flags.

## State And Persistence
No persisted state beyond exporter output; it observes process metrics through shell commands.

## Dependencies And Integration Points
Integrates with blobfuse2 health-monitor packages, shared `hmcommon` globals, monitor factory registration, named pipes, JSON/stat export files, and Azure Storage Fuse common logging/config packages.

## Risks
`top` output parsing is locale/platform sensitive, and `ExportStats` assumes non-empty strings before checking the last character.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/cpu_mem_profiler/cpu_mem_monitor.go -->
