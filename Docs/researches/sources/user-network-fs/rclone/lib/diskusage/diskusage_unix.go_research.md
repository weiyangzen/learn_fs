# sources/user-network-fs/rclone/lib/diskusage/diskusage_unix.go

## Purpose
This implementation covers common Unix-like platforms using `unix.Statfs`.

## Important APIs, types, and functions
- Build constraint: `aix || android || darwin || dragonfly || freebsd || ios || linux`.
- `New(dir string) (Info, error)` maps `unix.Statfs_t` fields into `Info`.

## Control flow
`New` calls `unix.Statfs`, returns errors directly, and computes byte counts as `Bfree * Bsize`, `Bavail * Bsize`, and `Blocks * Bsize`.

## State and persistence behavior
No state is persisted. The call reads current filesystem usage for the path.

## Dependencies and integration points
It depends on `golang.org/x/sys/unix` and provides the package API for Linux, macOS/iOS, Android, and several BSD-like systems.

## Risks and edge cases
Different platforms may define block fields with different signedness or widths, hence explicit conversion. Some filesystems report fragment sizes differently from block sizes; this implementation chooses `Bsize` consistently with its historical contract.

## Test signals
`diskusage_test.go` is the direct smoke test on these platforms.
