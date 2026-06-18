<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_oncreate.go -->
# sources/user-network-fs/go-nfs/nfs_oncreate.go

## Purpose
Implements NFS CREATE for regular files with unchecked and guarded modes.

## Important APIs, Types, and Functions
`onCreate` and create mode constants are central.

## Control Flow
The handler decodes directory/name and create mode, parses attributes or rejects exclusive mode, resolves the parent, checks write capability and name length, creates/closes the file, applies attributes, returns optional handle, post-op attrs, and directory WCC.

## State and Persistence Behavior
Persistent changes are file creation and metadata mutations in the backing billy filesystem plus a new cached handle.

## Dependencies and Integration Points
Depends on `SetFileAttributes`, `Handler.Change`, billy create/stat, and XDR.

## Risks and Edge Cases
Exclusive create is unsupported; post-op attrs call `tryStat(fs, []string{file.Name()})`, which may lose parent path; guarded semantics are minimal.

## Test Signals
CREATE tests should cover existing file guarded/unchecked behavior, exclusive rejection, attributes, and directory WCC.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_oncreate.go -->
