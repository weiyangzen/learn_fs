# sources/user-network-fs/rclone/lib/diskusage/diskusage_openbsd.go

## Purpose
This OpenBSD-specific implementation reports disk space using `unix.Statfs`.

## Important APIs, types, and functions
- Build constraint: `openbsd`.
- `New(dir string) (Info, error)` maps `unix.Statfs_t` fields into byte counts.

## Control flow
`New` calls `unix.Statfs`, returns syscall errors directly, and computes byte values from `F_bfree`, `F_bavail`, and `F_blocks` multiplied by `F_bsize`.

## State and persistence behavior
No state is stored. Results reflect current filesystem state for the given directory.

## Dependencies and integration points
It depends on `golang.org/x/sys/unix` and implements the common diskusage API for OpenBSD builds.

## Risks and edge cases
The mapping uses OpenBSD's `F_*` field names, which differ from other Unix variants. As with other implementations, large multiplications may overflow `uint64` only in extreme cases.

## Test signals
The generic diskusage test runs this implementation on OpenBSD and asserts sane totals.
