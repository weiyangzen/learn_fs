<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/newunionfs/unionfs_test.go -->
# sources/user-network-fs/go-fuse/newunionfs/unionfs_test.go

## Purpose
Tests the new union filesystem's branch lookup, deletion markers, promotion, readdir behavior, and selected POSIX compatibility cases.

## Important APIs, Types, and Functions
`newTestCase`, `testCase.Clean`, `TestBasic`, `TestDelete`, `TestDeleteMarker`, `TestCreate`, `TestPromote`, `TestReaddir*`, and `TestPosix` are the main test APIs.

## Control Flow
Each test creates temp `ro`, `rw`, and mount directories, mounts `unionFSRoot`, mutates the mounted view, and verifies effects in the backing trees or mounted paths.

## State and Persistence Behavior
Test state is isolated in temp dirs and a mounted FUSE server; `Clean` unmounts. `init` sets umask to zero for predictable modes.

## Dependencies and Integration Points
Depends on go-fuse mount support, `internal/testutil`, and the shared `posixtest` suite.

## Risks and Edge Cases
Tests require FUSE availability and can be flaky if unmount fails. Only a subset of POSIX tests is enabled, leaving rename, hard link, and directory mutation gaps.

## Test Signals
The file itself is the primary signal for unionfs regressions and should be run with verbose FUSE logging when debugging.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/newunionfs/unionfs_test.go -->
