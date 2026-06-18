<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/file/file_other.go -->
# sources/user-network-fs/go-nfs/file/file_other.go

## Purpose
Provides the fallback metadata extractor for unsupported platforms.

## Important APIs, Types, and Functions
`getOSFileInfo` always returns nil.

## Control Flow
Build tags select this file for platforms not otherwise handled.

## State and Persistence Behavior
Stateless.

## Dependencies and Integration Points
Used indirectly by `file.GetInfo`.

## Risks and Edge Cases
NFS fileids fall back to path hashes and ownership/specdata are unavailable on these platforms.

## Test Signals
Cross-compilation builds validate this fallback.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/file/file_other.go -->
