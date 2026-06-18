<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/platform_freebsd.go -->
# sources/user-network-fs/go-fuse/posixtest/platform_freebsd.go

## Purpose
Normalizes FreeBSD stat structures for cross-platform POSIX tests by clearing revision-specific spare fields.

## Important APIs, Types, and Functions
`clearStatRevision` copies an empty `syscall.Stat_t.Spare` over `unix.Stat_t.Spare`.

## Control Flow
Called before comparing `Stat_t` values in tests that otherwise expect stable metadata.

## State and Persistence Behavior
Stateless test helper.

## Dependencies and Integration Points
Used by `FstatDeleted` on FreeBSD; depends on `golang.org/x/sys/unix` and `syscall.Stat_t` layout.

## Risks and Edge Cases
If FreeBSD stat layout changes, the field adjustment could fail to compile or miss noisy fields.

## Test Signals
FreeBSD CI or `test-freebsd.bash` validates that deleted-file stat comparisons are not revision-noisy.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/platform_freebsd.go -->
