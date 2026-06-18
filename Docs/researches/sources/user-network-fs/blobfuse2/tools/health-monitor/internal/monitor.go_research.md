<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/internal/monitor.go -->
# sources/user-network-fs/blobfuse2/tools/health-monitor/internal/monitor.go

Source path: `sources/user-network-fs/blobfuse2/tools/health-monitor/internal/monitor.go`

## Purpose
Part of the blobfuse2 health-monitor command, which samples process, blobfuse stats, and cache activity and exports JSON telemetry.

## Important APIs, Types, And Functions
Package functions: none declared. Types: `Monitor`. Imports: none declared.

## Control Flow
Declares the common `Monitor` interface implemented by every monitor plugin: naming, validation, monitoring loop, and export hook.

## State And Persistence
No state; this is the contract tying main, factory, and monitor implementations together.

## Dependencies And Integration Points
Integrates with blobfuse2 health-monitor packages, shared `hmcommon` globals, monitor factory registration, named pipes, JSON/stat export files, and Azure Storage Fuse common logging/config packages.

## Risks
The interface has no context/cancellation parameter, so monitors rely on process death, pipe errors, or watcher closure to stop.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/internal/monitor.go -->
