<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/common/types.go -->
# sources/user-network-fs/blobfuse2/tools/health-monitor/common/types.go

Source path: `sources/user-network-fs/blobfuse2/tools/health-monitor/common/types.go`

## Purpose
Part of the blobfuse2 health-monitor command, which samples process, blobfuse stats, and cache activity and exports JSON telemetry.

## Important APIs, Types, And Functions
Package functions: none declared. Types: `CacheEvent`, `CpuMemStat`. Imports: `path/filepath`.

## Control Flow
Defines monitor names, output file constants, global flag-backed runtime settings, default paths, version, and the JSON-facing `CacheEvent` and `CpuMemStat` structures.

## State And Persistence
Stores process-wide configuration in package globals populated by CLI flags or config integration.

## Dependencies And Integration Points
Integrates with blobfuse2 health-monitor packages, shared `hmcommon` globals, monitor factory registration, named pipes, JSON/stat export files, and Azure Storage Fuse common logging/config packages.

## Risks
Global mutable configuration couples all monitors and makes isolated tests or multiple monitor instances difficult.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/common/types.go -->
