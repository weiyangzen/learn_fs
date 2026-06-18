<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/imports.go -->
# sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/imports.go

Source path: `sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/imports.go`

## Purpose
Part of the blobfuse2 health-monitor command, which samples process, blobfuse stats, and cache activity and exports JSON telemetry.

## Important APIs, Types, And Functions
Package functions: none declared. Types: none declared. Imports: `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/monitor/blobfuse_stats`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/monitor/cpu_mem_profiler`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/monitor/file_cache`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/monitor/network_profiler`.

## Control Flow
Blank-imports every concrete monitor package so their `init` functions can self-register with the internal factory.

## State And Persistence
No direct state, but import side effects populate the monitor registry.

## Dependencies And Integration Points
Integrates with blobfuse2 health-monitor packages, shared `hmcommon` globals, monitor factory registration, named pipes, JSON/stat export files, and Azure Storage Fuse common logging/config packages.

## Risks
Removing or build-tagging this file can leave monitors unregistered even though their packages compile.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/imports.go -->
