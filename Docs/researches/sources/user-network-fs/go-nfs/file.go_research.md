<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/file.go -->
# sources/user-network-fs/go-nfs/file.go

## Purpose
Defines NFS file metadata conversion, weak-cache-consistency helpers, and parsing/applying NFS setattr requests.

## Important APIs, Types, and Functions
Key types/functions are `FileAttribute`, `FileType`, `FileCacheAttribute`, `ToFileAttribute`, `tryStat`, `WriteWcc`, `WritePostOpAttrs`, `SetFileAttributes`, `Apply`, `Mode`, and `ReadSetFileAttributes`.

## Control Flow
Handlers convert billy `os.FileInfo` into NFS attributes, parse optional sattr fields from XDR, apply requested changes through `billy.Change`, and encode pre/post attribute presence wrappers.

## State and Persistence Behavior
No global state; operations mutate backing files through `Chmod`, `Lchown`, `Chtimes`, opening/truncating files, and derive attributes from current stat calls.

## Dependencies and Integration Points
Used by nearly all NFS procedures; depends on billy, the internal `file` metadata package, XDR, and OS error mapping.

## Risks and Edge Cases
`Apply` returns nil for some unknown `Lstat` errors, time pointer comparison is by pointer not value in one check, and truncation opens with `O_EXCL` in a questionable way.

## Test Signals
Procedure tests for setattr, create, mkdir, write, wcc bodies, symlinks, and platform stat metadata cover this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/file.go -->
