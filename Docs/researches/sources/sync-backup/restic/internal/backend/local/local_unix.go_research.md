<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/local_unix.go -->
# sources/sync-backup/restic/internal/backend/local/local_unix.go

## Purpose
Provides Unix-specific helpers for directory fsync, macOS ENOTTY handling, read-only chmod, and file removal.

## Important APIs, Types, And Functions
fsyncDir, isMacENOTTY, setFileReadonly, and removeFile are the API used by local.go.

## Control Flow
fsyncDir opens and syncs a directory; setFileReadonly clears write bits; removeFile chmods write permission back before removing.

## State And Persistence Behavior
Mutates filesystem permissions and sync state; no repository metadata beyond file mode changes.

## Dependencies And Integration Points
Depends on os, runtime/syscall behavior, and internal/errors.

## Risks And Edge Cases
Risks are platform-specific syscall errors and filesystems that do not support directory fsync or chmod semantics.

## Test Signals
Covered indirectly by local backend tests and platform-specific CI.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/local_unix.go -->
