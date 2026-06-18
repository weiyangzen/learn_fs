# sources/security-integrity/gocryptfs/tests/test_helpers/helpers.go

## Purpose
Shared Go test utility package for gocryptfs integration tests. It owns temp directory setup, filesystem initialization, hashing, size checks, common operation tests, control-socket queries, disk-usage helpers, and command exit-code decoding.

## Important APIs, Types, And Functions
- `doInit` initializes `TmpDir`, `DefaultPlainDir`, `DefaultCipherDir`, `MountInfo`, and `X255`.
- `ResetTmpDir` removes prior mounts/content and recreates default dirs, optionally writing `gocryptfs.diriv`.
- `InitFS` runs `../../gocryptfs -init` with fast scrypt settings.
- `Md5fn`, `Md5hex`, `VerifySize`, `VerifyExistence`, and `Du` provide assertions.
- `TestMkdirRmdir` and `TestRename` are reusable behavior checks.
- `QueryCtlSock` wraps `ctlsock.New` and query error handling.
- `ExtractCmdExitCode` normalizes exec and path errors to integer codes.

## Control Flow
Package init creates a user-specific parent temp dir and unique test temp dir. Tests call reset/init helpers, then mount helpers from the companion file. Assertion helpers combine high-level reads with low-level stat/fstat or directory enumeration to catch FUSE inconsistencies.

## State And Persistence
Global state includes temp paths and `MountInfo`. `ResetTmpDir` can unmount busy child dirs before deleting them, making it both setup and cleanup.

## Dependencies And Integration Points
Depends on gocryptfs internal packages `nametransform` and `syscallcompat`, the `ctlsock` package, external gocryptfs binary, and OS temp/filesystem behavior.

## Risks And Edge Cases
Because helpers panic on unexpected cleanup errors, stale mounts can fail unrelated tests. MD5 helpers read whole files into memory and are unsuitable for very large data.

## Test Signals
Signals are consumed by callers: consistent size/read/stat/fstat, consistent existence across stat/open/readdir, successful control socket responses, and reusable operation assertions.
