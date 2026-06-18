<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_filesystem.go -->
# sources/sync-backup/kopia/cli/storage_filesystem.go

## Purpose
Implements filesystem repository storage flags and option conversion.

## Important APIs, Types, And Functions
Important symbols are `storageFilesystemFlags`, `Setup`, `Connect`, `initialDirectoryShards`, `getIntPtrValue`, `getFileModeValue`, and provider `init`.

## Control Flow
Setup registers path, ownership, file/dir mode, flat layout, list parallelism, and throttling flags. Connect resolves a user-friendly path, requires it to be absolute, parses optional UID/GID and octal modes, selects sharding based on flat/format version, and calls `filesystem.New`.

## State And Persistence Behavior
Persistent behavior is creation/use of repository files on local filesystem with selected modes, ownership, sharding, and throttling. Parsed invalid UID/mode values silently fall back to nil/default.

## Dependencies And Integration Points
Integrates filesystem blob backend, ospath resolution, storage registry, throttling flags, and repository format-version compatibility.

## Risks And Edge Cases
Silent parse fallback can hide bad owner/mode input. Format version 1 forces `{3,3}` sharding for old-client compatibility, while later versions defer to backend defaults unless flat is set.

## Test Signals
Tests should cover absolute path enforcement, user-friendly path resolution, flat/version sharding, mode/owner parsing, and defaults.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_filesystem.go -->
