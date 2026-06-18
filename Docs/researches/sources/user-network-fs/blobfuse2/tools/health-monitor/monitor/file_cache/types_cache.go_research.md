<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/file_cache/types_cache.go -->
# sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/file_cache/types_cache.go

Source path: `sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/file_cache/types_cache.go`

## Purpose
Part of the blobfuse2 health-monitor command, which samples process, blobfuse stats, and cache activity and exports JSON telemetry.

## Important APIs, Types, And Functions
Package functions: none declared. Types: none declared. Imports: none declared.

## Control Flow
Defines string constants used by the file-cache monitor for watcher operation names and JSON value keys.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Integrates with blobfuse2 health-monitor packages, shared `hmcommon` globals, monitor factory registration, named pipes, JSON/stat export files, and Azure Storage Fuse common logging/config packages.

## Risks
Constants must match `watcher.Event.Op.String()` upper-case output; library changes can silently stop event classification.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/file_cache/types_cache.go -->
