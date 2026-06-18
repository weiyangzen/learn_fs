<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/cpu_mem_profiler/cpu_mem_monitor_test.go -->
# sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/cpu_mem_profiler/cpu_mem_monitor_test.go

Source path: `sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/cpu_mem_profiler/cpu_mem_monitor_test.go`

## Purpose
Part of the blobfuse2 health-monitor command, which samples process, blobfuse stats, and cache activity and exports JSON telemetry.

## Important APIs, Types, And Functions
Package functions: `SetupTest`, `TestGetCpuMemoryUsage`, `TestGetCpuMemoryUsageFailure`, `TestCpuMemMonitor`. Types: `cpuMemMonitorTestSuite`. Imports: `fmt`, `os`, `testing`, `github.com/Azure/azure-storage-fuse/v2/common`, `github.com/Azure/azure-storage-fuse/v2/common/log`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/common`, `github.com/stretchr/testify/assert`, `github.com/stretchr/testify/suite`.

## Control Flow
Testify suite initializes logging and temp globals, tests successful and failed CPU/memory parsing, and exercises monitor construction/validation.

## State And Persistence
Mutates process-level health-monitor globals during setup.

## Dependencies And Integration Points
Integrates with blobfuse2 health-monitor packages, shared `hmcommon` globals, monitor factory registration, named pipes, JSON/stat export files, and Azure Storage Fuse common logging/config packages.

## Risks
Tests depend on local process/table behavior and may be brittle across operating systems or `top` variants.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/cpu_mem_profiler/cpu_mem_monitor_test.go -->
