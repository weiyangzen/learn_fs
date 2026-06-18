<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/newunionfs/unionfs.go -->
# sources/user-network-fs/go-fuse/newunionfs/unionfs.go

## Purpose
Implements a writable-over-readonly union filesystem using go-fuse's inode API and deletion marker files in the writable branch.

## Important APIs, Types, and Functions
Important pieces are `unionFSRoot`, `unionFSNode`, marker helpers, `Lookup`, `Readdir`, `Create`, `Open`, `Setattr`, deletion operations, `promote`, and `promoteRegularFile`.

## Control Flow
Reads search branches unless a deletion marker hides the path. Writes and metadata changes promote lower-branch files/directories into the writable branch, then operate there. Deletes unlink writable files or create marker files for lower entries.

## State and Persistence Behavior
Persistent state lives in the writable root: promoted copies and `DELETIONS/<hash>-<base>` marker files. Inode state is go-fuse runtime state derived from branch lookups.

## Dependencies and Integration Points
Depends on `github.com/hanwen/go-fuse/v2/fs`, `fuse`, loopback files, raw syscalls, path hashing, and POSIX metadata operations.

## Risks and Edge Cases
Promotion handles regular files and directories but panics on other modes; marker hashes can collide in theory; path/time handling has rough edges; setattr has a dead `fh` type assertion branch after a nil check.

## Test Signals
`unionfs_test.go` covers create, delete, marker removal, readdir merging, promotion, and selected `posixtest` cases. More tests should cover symlink promotion, xattrs, hard links, and marker collisions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/newunionfs/unionfs.go -->
