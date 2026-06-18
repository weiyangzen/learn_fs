<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/fileswriter.go -->
# sources/sync-backup/restic/internal/restorer/fileswriter.go

## Purpose
Manages concurrent low-level writes to restored files while safely creating, replacing, sizing, caching, and closing file handles.

## Important APIs and Control Flow
`filesWriter`, `filesWriterBucket`, `partialFile`, `newFilesWriter`, `openFile`, `createFile`, `ensureSize`, `writeToFile`, and `flush` are the main APIs. `writeToFile` hashes paths into buckets, reuses active or LRU-cached file handles, writes with `WriteAt`, and releases handles back to cache when no users remain. `createFile` handles read-only targets, symlinks, directories, hardlinked files, recursive deletion policy, no-follow opens, exclusive replacement, preallocation, and sparse truncation.

## State, Persistence, Dependencies, and Integration
State is process-local: bucket maps, reference counts, sparse flags, and an LRU cache. It integrates with `internal/fs`, platform truncate helpers, xxhash, and simplelru; persistence is the target filesystem content and metadata side effects.

## Risks and Test Signals
Risks are TOCTOU/path replacement issues, leaking handles under errors, platform-specific readonly and directory behavior, and corrupting hardlinked existing files. Tests cover basic writes/cache behavior, replacing directories/symlinks/hardlinks, recursive delete policy, sparse sizing, and platform-specific directory-not-empty errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/fileswriter.go -->
