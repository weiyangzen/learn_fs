<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onmkdir.go -->
# sources/user-network-fs/go-nfs/nfs_onmkdir.go

## Purpose
Implements NFS MKDIR.

## Important APIs, Types, and Functions
`onMkdir` and `mkdirDefaultMode` are central.

## Control Flow
It decodes parent/name and attributes, resolves parent, checks write capability/name/special dot names/existing path, creates the directory with requested or default mode, applies attributes when possible, and returns handle, attrs, and parent WCC.

## State and Persistence Behavior
Persistent state is a new directory and metadata changes.

## Dependencies and Integration Points
Depends on billy `MkdirAll`, handler change support, and XDR.

## Risks and Edge Cases
Default mode is `755` decimal, not octal `0755`, which likely creates wrong permissions. `MkdirAll` may create missing parents instead of strict single-level mkdir.

## Test Signals
MKDIR tests should assert mode bits, existing-file/dir errors, dot-name rejection, and parent WCC.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onmkdir.go -->
