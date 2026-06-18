<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/file/file_unix.go -->
# sources/user-network-fs/go-nfs/file/file_unix.go

## Purpose
Extracts Unix stat metadata for common Unix-like platforms.

## Important APIs, Types, and Functions
`getOSFileInfo` reads `*syscall.Stat_t` and returns nlink, uid, gid, `unix.Major/Minor(Rdev)`, and inode fileid.

## Control Flow
Called by `GetInfo` after a filesystem stat.

## State and Persistence Behavior
Stateless conversion.

## Dependencies and Integration Points
Feeds NFS attributes for Unix exports and special devices.

## Risks and Edge Cases
Assumes `FileInfo.Sys()` is `*syscall.Stat_t`; virtual filesystems returning other payloads fall back to path hashes.

## Test Signals
Unix tests should verify inode/fileid stability and device major/minor on special nodes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/file/file_unix.go -->
