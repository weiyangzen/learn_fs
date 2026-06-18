<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/xfstests.go -->
# sources/user-network-fs/go-fuse/posixtest/xfstests.go

## Purpose
Ports an xfstests directory offset seek case into the POSIX suite.

## Important APIs, Types, and Functions
`DirSeek` creates many entries, captures raw dirents, seeks to each previous offset, and verifies the next dirent matches.

## Control Flow
It uses `readAllDirEntries`, `unix.Seek`, and `unix.ReadDirent` to validate stable `d_off` handling in directory streams.

## State and Persistence Behavior
State is the `ttt` directory and 168 files under the supplied root.

## Dependencies and Integration Points
Depends on raw getdents parsing through go-fuse `fuse.DirEntry`.

## Risks and Edge Cases
Directory offset behavior is subtle across kernels and FUSE implementations; incorrect offsets can cause repeated, skipped, or zero entries after seek.

## Test Signals
Included in the `All` registry and particularly useful for regressions around readdir cookies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/xfstests.go -->
