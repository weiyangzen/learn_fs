<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/file_cache/cache_monitor.go -->
# sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/file_cache/cache_monitor.go

Source path: `sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/file_cache/cache_monitor.go`

## Purpose
Part of the blobfuse2 health-monitor command, which samples process, blobfuse stats, and cache activity and exports JSON telemetry.

## Important APIs, Types, And Functions
Package functions: `GetName`, `SetName`, `Monitor`, `ExportStats`, `Validate`, `cacheWatcher`, `createEvent`, `removeEvent`, `chmodEvent`, `writeEvent`, `renameEvent`, `moveEvent`, `getCacheEventObj`, `NewFileCacheMonitor`, `init`. Types: `FileCache`, `CacheDir`. Imports: `fmt`, `math`, `strconv`, `strings`, `time`, `github.com/Azure/azure-storage-fuse/v2/common`, `github.com/Azure/azure-storage-fuse/v2/common/log`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/common`, `github.com/Azure/azure-storage-fuse/v2/tools/health-monitor/internal`, `github.com/radovskyb/watcher`.

## Control Flow
Validates pid and cache path, sets a recursive watcher over the file-cache directory, converts CREATE/REMOVE/CHMOD/RENAME/MOVE events into `CacheEvent` payloads, updates size/eviction counters, and exports timestamped events.

## State And Persistence
Maintains in-memory maps of created and removed files plus aggregate cache bytes/percentage. The watcher observes the configured cache directory and emits JSON via the exporter.

## Dependencies And Integration Points
Integrates with blobfuse2 health-monitor packages, shared `hmcommon` globals, monitor factory registration, named pipes, JSON/stat export files, and Azure Storage Fuse common logging/config packages.

## Risks
Map updates happen in the watcher goroutine without explicit synchronization; cache-size accounting can be inaccurate if events are missed, reordered, or represent directories. `maxSizeMB` of zero risks divide-by-zero style output.

## Test Signals
Primary signals are `go test` pass/fail status, asserted error strings and file contents, MD5/integrity checks, benchmark/stress throughput logs, JSON monitor output, and cleanup behavior that leaves no active mount or residual test tree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/tools/health-monitor/monitor/file_cache/cache_monitor.go -->
