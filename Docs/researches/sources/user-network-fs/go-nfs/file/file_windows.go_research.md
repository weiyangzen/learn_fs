<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/file/file_windows.go -->
# sources/user-network-fs/go-nfs/file/file_windows.go

## Purpose
Provides the Windows metadata extractor fallback.

## Important APIs, Types, and Functions
`getOSFileInfo` currently returns nil, with a comment noting possible future Windows API support.

## Control Flow
No runtime control flow beyond returning nil.

## State and Persistence Behavior
Stateless.

## Dependencies and Integration Points
Used by `file.GetInfo` on Windows.

## Risks and Edge Cases
NFS attributes lack nlink/uid/gid/inode and fall back to path-derived fileids in callers.

## Test Signals
Windows build tests validate compilation; behavior tests would need custom metadata support.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/file/file_windows.go -->
