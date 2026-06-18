<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/platform_unix.go -->
# sources/user-network-fs/go-fuse/posixtest/platform_unix.go

## Purpose
Provides the no-op implementation of stat normalization for non-FreeBSD POSIX tests.

## Important APIs, Types, and Functions
`clearStatRevision` accepts `*unix.Stat_t` and does nothing.

## Control Flow
Build tags select this file outside FreeBSD.

## State and Persistence Behavior
Stateless helper.

## Dependencies and Integration Points
Used by shared tests to compile uniformly across Unix-like systems.

## Risks and Edge Cases
If another platform gains volatile stat fields, comparisons may become flaky until this helper is specialized.

## Test Signals
Linux and Darwin POSIX runs indirectly exercise this no-op path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/platform_unix.go -->
