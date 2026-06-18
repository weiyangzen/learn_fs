# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/file.c

Read status: complete, 610 lines.

`file.c` implements `sam`’s `File` object, edit logging, undo/redo, name changes, dot/mark logging, buffer loading, update synchronization, and cleanup.

Undo records are stored backward in `delta` and `epsilon` buffers, with associated inserted text or filenames preceding each `Undo` structure. `loginsert` and `logdelete` merge nearby edits into one undo record through `merge`. `filemark` snapshots sequence, dot, mark, and modification state before a new edit sequence.

`fileundo` reverses `delta` or `epsilon` records, applying deletes, inserts, filename restores, dot restores, and mark restores while syncing terminal state through rasp calls. `fileupdate` flushes pending merge state and applies logged changes to the file buffer and UI.

`filesetname`, `fileunsetname`, `fileload`, `filereadc`, `filereset`, and `fileclose` provide file lifecycle operations.

Filesystem relevance: core editor abstraction for file contents and metadata, backed by buffers and eventually used by disk/file I/O.
