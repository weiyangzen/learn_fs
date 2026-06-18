# sources/sync-backup/restic/internal/fs/preallocate_linux.go

Purpose: Linux file preallocation using `fallocate`.

Important APIs: `PreallocateFile` and `ignoringEINTR`.

Control flow and state: Returns nil for non-positive sizes. For positive sizes, calls `unix.Fallocate(fd, 0, 0, size)` and retries on `EINTR`.

Dependencies and integration: Used by restore/output writers that can benefit from reserved disk space and known file length.

Risks: Filesystems can return `ENOTSUP`, and allocation mode changes file size. EINTR handling is copied from Go internals and should remain simple.

Test signals: `preallocate_test.go` checks resulting size or allocated blocks and skips unsupported filesystems.
