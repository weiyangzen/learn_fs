<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/truncate_other.go -->
# sources/sync-backup/restic/internal/restorer/truncate_other.go

## Purpose
Provides the default sparse truncation implementation for non-Windows platforms.

## Important APIs and Control Flow
`truncateSparse` delegates to file truncation to set logical size while preserving sparseness where the filesystem supports holes. Control flow is a thin platform shim called by `ensureSize` when sparse restore is requested.

## State, Persistence, Dependencies, and Integration
Persistent state is the target file size and sparse allocation. Integration is through `fileswriter.go`.

## Risks and Test Signals
Risks are filesystem-specific sparse behavior and errors from unsupported operations; sparse restore tests provide integration signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/truncate_other.go -->
