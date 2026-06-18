# sources/sync-backup/restic/cmd/restic/integration_helpers_unix_test.go

Purpose: Unix-specific implementations for integration directory comparison and hardlink grouping.

Important APIs/types/functions: `(*dirEntry).equals`; `nlink`; `createFileSetPerHardlink`.

Control flow and state: equality checks path, mode, modification time, UID, GID, and link count using `syscall.Stat_t`. `nlink` extracts link count. `createFileSetPerHardlink` groups directory entries by inode number.

Dependencies and integration points: used by shared integration helpers and restore tests on non-Windows platforms. Depends on syscall stat fields and filepath.

Risks: UID/GID and link-count comparisons can be sensitive to filesystem behavior and privilege. Symlink modtime handling is delegated to shared `sameModTime`.

Test signals: indirectly exercised by restore directory diff tests and hardlink-related tests elsewhere.
