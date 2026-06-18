<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/dirtree/dirtree.go -->
# sources/user-network-fs/rclone/fs/dirtree/dirtree.go

## Purpose
Builds an in-memory directory tree mapping directory paths to their child `fs.DirEntries`.

## Important APIs, Types, And Control Flow
`DirTree` is `map[string]fs.DirEntries`. `Add` inserts an entry under its parent, `AddDir` also ensures the directory has a key, and `AddEntry` adds files/directories plus missing parents. `Find` searches a parent slice. `checkParent` and `CheckParents` synthesize missing parent `fs.Dir` entries. `Sort`, `Dirs`, `Prune`, and `String` provide deterministic traversal, subtree removal, and display.

## State And Persistence
All state is in-memory map/slices. Synthesized parents use `time.Now()` modtimes. `Prune` mutates both the tree and the caller-provided directory map.

## Dependencies And Integration Points
Depends on `fs.DirEntries`, `fs.NewDir`, and path utilities. Used by recursive listing and sync logic that needs a materialized hierarchy.

## Risks And Test Signals
`Find` is O(N), and `Prune` deliberately mutates during map iteration to avoid recursion. Unknown entry types cause errors or panic depending on path. Tests cover add, parent synthesis, sorting, dirs, pruning, and a parent-check benchmark.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/dirtree/dirtree.go -->
