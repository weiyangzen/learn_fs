# sources/sync-backup/restic/internal/fs/node_linux_test.go

Purpose: Linux-specific regression test for symlink timestamp restore errors.

Important APIs: `TestRestoreSymlinkTimestampsError`.

Control flow and state: Creates a symlink-type node, calls `nodeRestoreTimestamps` on a nonexistent path, and asserts `fs.ErrNotExist` plus path context.

Dependencies and integration: Validates `node_linux.go` and the error wrapping from `nodeRestoreTimestamps`.

Risks: Narrow test; successful timestamp preservation is covered indirectly by broader node restore tests.

Test signals: Ensures Linux no-follow timestamp calls surface useful missing-path errors.
