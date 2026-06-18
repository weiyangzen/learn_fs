<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/local_windows.go -->
# sources/sync-backup/restic/internal/backend/local/local_windows.go

## Purpose
Provides Windows-specific local backend helpers.

## Important APIs, Types, And Functions
fsyncDir, isMacENOTTY, setFileReadonly, and removeFile match the Unix helper API.

## Control Flow
Directory fsync is a no-op; setFileReadonly clears owner write bit; removeFile chmods writable then removes.

## State And Persistence Behavior
Mutates Windows-visible file mode bits through os.Chmod/remove.

## Dependencies And Integration Points
Depends on os and internal/errors.

## Risks And Edge Cases
Windows permission semantics differ from Unix; helper behavior is deliberately minimal.

## Test Signals
Covered indirectly by local backend tests on Windows CI.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/local_windows.go -->
