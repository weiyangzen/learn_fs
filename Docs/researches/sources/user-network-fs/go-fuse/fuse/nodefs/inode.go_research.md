## sources/user-network-fs/go-fuse/fuse/nodefs/inode.go

Purpose: nodefs in-memory inode tree representation and child/file bookkeeping.

Important APIs/types/functions: `parentData`, `Inode`, `newInode`, `String`, `AnyFile`, `Children`, `Parent`, `FsChildren`, `Node`, `Files`, `IsDir`, `NewChild`, `GetChild`, `AddChild`, `TreeWatcher`, `RmChild`, `addChild`, `rmChild`, `mountFs`, `canUnmount`, `getMountDirEntries`, and `verify`.

Control flow: nodes add/remove children under tree locks, maintain parent references, track open files, and expose snapshots to readers. Mount helpers annotate inodes with mount metadata and verify invariants when paranoia is enabled.

State and persistence: all inode tree, child maps, parent links, and open file slices are in memory.

Dependencies and integration: used throughout nodefs connector and pathfs translation.

Risks and test signals: concurrent mutation, stale parent data, and unmount with active files are primary risks. Memnode and connector tests exercise these structures.
