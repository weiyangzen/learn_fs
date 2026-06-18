<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/local.go -->
# sources/sync-backup/restic/internal/backend/local/local.go

## Purpose
Implements the local filesystem backend for restic repositories.

## Important APIs, Types, And Functions
Local, NewFactory, open/Open/Create, Properties, Hasher, IsNotExist, IsPermanentError, Save, Load/openReader, Stat, Remove, List, Delete, Close, Warmup/WarmupWait, and traversal helpers are the important API.

## Control Flow
Create builds all layout directories after checking config absence. Save writes to a temp file, optionally preallocates, copies exact bytes, fsyncs file, closes, renames atomically, fsyncs directory, and makes the file read-only. Load delegates to util.DefaultLoad with offset/length validation in openReader. List walks base dirs or pack subdirs and feeds regular files to the callback.

## State And Persistence Behavior
Persists repository files on the local filesystem using DefaultLayout. Modes are derived from existing config or defaults; temp files are cleaned after errors.

## Dependencies And Integration Points
Depends on os/syscall/path/filepath/io, backend/layout/limiter/location/util, fs preallocation, backoff, and platform helpers in local_unix.go/local_windows.go.

## Risks And Edge Cases
Risks include filesystem-specific fsync/chmod behavior, partial temp files, ENOSPC/permanent error classification, short reads, and concurrent directory creation. Atomic replace is advertised as true due rename behavior.

## Test Signals
Covered by local tests, backend suite usage, layout fixture tests, and internal temp-file failure tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/local.go -->
