# sources/sync-backup/restic/internal/fs/node_freebsd.go

Purpose: FreeBSD-specific node helpers.

Important APIs: `nodeRestoreSymlinkTimestamps` and `mknod`.

Control flow and state: Symlink timestamp restore helper is a no-op. `mknod` calls `syscall.Mknod` and wraps errors with `*os.PathError`.

Dependencies and integration: Provides platform hooks used by generic node restore/create code on FreeBSD.

Risks: Symlink timestamp preservation is intentionally unsupported here. Device creation keeps normal privilege constraints.

Test signals: Unix node tests cover mknod-style error wrapping where applicable; generic restore tests account for BSD symlink timestamp limitations.
