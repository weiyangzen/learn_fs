<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/internal/factory.go -->
# sources/user-network-fs/blobfuse2/tools/health-monitor/internal/factory.go

Source path: `sources/user-network-fs/blobfuse2/tools/health-monitor/internal/factory.go`

## Purpose
Part of the blobfuse2 health-monitor command, which samples process, blobfuse stats, and cache activity and exports JSON telemetry.

## Important APIs, Types, And Functions
Package functions: `GetMonitor`, `AddMonitor`, `init`. Types: `NewMonitor`. Imports: `fmt`.

## Control Flow
Maintains a package-level registry from monitor name to constructor. Monitor packages register themselves in `init`; `GetMonitor` instantiates by name for main.

## State And Persistence
The registry map is process-global and mutable during package initialization.

## Dependencies And Integration Points
Integrates with blobfuse2 health-monitor packages, shared `hmcommon` globals, monitor factory registration, named pipes, JSON/stat export files, and Azure Storage Fuse common logging/config packages.

## Risks
There is no locking around registration or lookup, so the design assumes single-threaded init-time registration.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/internal/factory.go -->
