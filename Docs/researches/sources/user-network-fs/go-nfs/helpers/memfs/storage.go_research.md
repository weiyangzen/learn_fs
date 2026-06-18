<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/helpers/memfs/storage.go -->
# sources/user-network-fs/go-nfs/helpers/memfs/storage.go

## Purpose
Stores the backing tree for the helper memfs implementation.

## Important APIs, Types, and Functions
`storage`, `newStorage`, `New`, `Get`, `Children`, `Rename`, `move`, `Remove`, `clean`, and `content.ReadAt/WriteAt` are important.

## Control Flow
`New` creates files and recursively ensures parents. `Rename` builds a list of paths to move and updates file/children maps. `content` protects byte access with an RW mutex.

## State and Persistence Behavior
Persistent state is `files` and `children` maps plus each file's shared content buffer.

## Dependencies and Integration Points
Used exclusively by `memfs.go` behind billy filesystem methods.

## Risks and Edge Cases
Map operations are unsynchronized; directory rename prefix matching can catch paths with similar prefixes; `WriteAt` casts offsets into slice bounds and needs careful large-offset handling.

## Test Signals
Memfs-focused tests should exercise nested rename/remove, directory children consistency, sparse writes, negative offsets, and race detection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/helpers/memfs/storage.go -->
