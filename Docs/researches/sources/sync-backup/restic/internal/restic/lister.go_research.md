<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/lister.go -->
# sources/sync-backup/restic/internal/restic/lister.go

## Purpose
Implements an in-memory wrapper for a repository/backend lister so a single `List` result can be replayed without re-querying storage.

## Important APIs and Control Flow
`fileInfo`, `memorizedLister.List`, and `MemorizeList` are the important pieces. `MemorizeList` detects an already-memoized lister, otherwise collects `(ID,size)` pairs for exactly one `FileType`. `memorizedLister.List` rejects mismatched file types, iterates the cached slice, forwards each pair to the callback, and stops on callback or context errors.

## State, Persistence, Dependencies, and Integration
State is a process-local slice plus the memoized file type; nothing is persisted. It depends only on `context`, `fmt`, and the repository `Lister`/`FileType` contracts and is used by callers that need stable repeated list iteration.

## Risks and Test Signals
The cache can become stale if the backend changes after memoization, and it is scoped to one file type. Tests verify replay, file-type mismatch errors, idempotent wrapping behavior, and source-list error propagation.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/lister.go -->
