# sources/sync-backup/restic/internal/fuse/dir.go

Purpose: Implements FUSE directory nodes backed by restic repository trees.

Important APIs: `dir`, `cleanupNodeName`, `newDir`, `unwrapCtxCanceled`, `replaceSpecialNodes`, `newDirFromSnapshot`, `open`, `Attr`, `calcNumberOfLinks`, `ReadDirAll`, `Lookup`, `Listxattr`, `Getxattr`, and `Forget`.

Control flow and state: Directories lazily load their tree once under a mutex into `items`. Special directory nodes named `.` or `/` with subtrees are replaced by their subtree contents. `ReadDirAll` emits `.`/`..` plus entries with inode/type. `Lookup` uses a tree cache to create child FUSE nodes by restic node type. `Forget` calls the inode cache cleanup callback.

Dependencies and integration: Uses `anacrolix/fuse`, restic `data.LoadTree`, repository blob loading, node-to-inode helpers, xattr helpers, and child node constructors (`newFile`, `newLink`, `newOther`).

Risks: Lazy tree loading must handle concurrent FUSE calls and context cancellation correctly. `calcNumberOfLinks` depends on `items` being loaded; callers typically call it after open for listings, but `Attr` can run before open. Duplicate cleaned names overwrite earlier entries.

Test signals: No direct tests in this subset; behavior is exercised by FUSE integration tests elsewhere. Interface assertions verify required FUSE contracts at compile time.
