# sources/sync-backup/restic/internal/fs/node_unix_test.go

Purpose: Unix-only tests for node metadata extraction, mknod error wrapping, and ownership restore.

Important APIs: `TestNodeFromFileInfo`, `TestMknodError`, and `TestLchown`.

Control flow and state: Reads metadata for source files, symlinks, `/dev/null`, and optionally `/dev/sda`; compares stat fields, device IDs, sizes, ownership, and timestamps. Ownership is tested by UID/GID and by user/group name.

Dependencies and integration: Validates `ExtendedStat`, `ToNode`, `mknod`/`mkfifo`, `lchown`, and user/group lookup integration.

Risks: Device-file tests are skipped if paths are unavailable; macOS/Solaris skip `/dev/null` xattr quirks.

Test signals: Strong Unix stat-to-node fidelity coverage.
