# sources/user-network-fs/rclone/lib/diskusage/diskusage_netbsd.go

## Purpose
This NetBSD-specific implementation reports disk space by calling `unix.Statvfs`.

## Important APIs, types, and functions
- Build constraint: `netbsd`.
- `New(dir string) (Info, error)` fills `Info` from `unix.Statvfs_t`.

## Control flow
`New` calls `unix.Statvfs(dir, &statfs)`, propagates errors, and multiplies block counts by `Bsize` for free, available, and total bytes.

## State and persistence behavior
No state is persisted. The returned values are a point-in-time filesystem snapshot.

## Dependencies and integration points
It depends on `golang.org/x/sys/unix`. It satisfies the shared `diskusage.New` API on NetBSD.

## Risks and edge cases
Block-field sizes vary by OS, which is why values are explicitly cast to `uint64`. Multiplication can theoretically overflow on extremely large filesystems, matching the package's unsigned-byte-count model.

## Test signals
`diskusage_test.go` will exercise this file only on NetBSD, checking nonzero total and ordering relationships.
