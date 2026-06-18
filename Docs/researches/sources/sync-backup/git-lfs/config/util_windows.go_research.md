<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/util_windows.go -->
# sources/sync-backup/git-lfs/config/util_windows.go

## Research

This Windows-only file implements `umask()` as a constant `077` because Windows lacks a POSIX umask syscall and owner bits are the meaningful chmod component. It feeds the same `Configuration.getMask` and `RepositoryPermissions` paths as Unix.

There is no mutable state or external I/O. The risk is semantic approximation: shared repository modes on Windows cannot mirror Unix group/world semantics exactly, and tests relying on exact modes must account for build tags.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/util_windows.go -->
