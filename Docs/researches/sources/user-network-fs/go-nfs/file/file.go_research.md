<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/file/file.go -->
# sources/user-network-fs/go-nfs/file/file.go

## Purpose
Defines portable extraction of non-standard stat metadata from `os.FileInfo`.

## Important APIs, Types, and Functions
`FileInfo` carries nlink, uid, gid, device major/minor, and fileid; `GetInfo` checks custom `Sys()` payloads then delegates to platform code.

## Control Flow
Callers pass `os.FileInfo`; the function returns platform metadata when available or nil when unsupported.

## State and Persistence Behavior
Stateless conversion helper.

## Dependencies and Integration Points
Used by `nfs.ToFileAttribute` to populate NFS nlink, owner, specdata, and fileid.

## Risks and Edge Cases
Fallback hashing in callers is less stable than real inode data; custom `Sys()` values must match this package's type.

## Test Signals
Metadata tests should feed both real OS stats and synthetic `file.FileInfo` payloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/file/file.go -->
