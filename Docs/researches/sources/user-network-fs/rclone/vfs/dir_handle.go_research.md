# sources/user-network-fs/rclone/vfs/dir_handle.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/dir_handle.go -->
## sources/user-network-fs/rclone/vfs/dir_handle.go

Purpose: represents an open VFS directory handle and implements directory read APIs.

Important APIs and control flow: `newDirHandle(d)` stores the directory. `String`, `Stat`, and `Node` expose handle identity. `Readdir(n)` lazily calls `d.ReadDirAll()`, converts nodes to `os.FileInfo`, stores the remaining slice in `fh.fis`, and returns either all entries (`n <= 0`) or the next chunk (`n > 0`), returning `io.EOF` only when a positive-size read finds no entries left. `Readdirnames(n)` maps `Readdir` results to names. `Close()` clears cached file infos.

State, dependencies, and integration: state is the directory pointer and cursor slice. It embeds `baseHandle` from the VFS package and depends on `io` and `os`. It integrates with mounted filesystem directory listing operations.

Risks and test signals: `DirHandle` is not synchronized for concurrent reads. It snapshots entries on first read and does not see later directory changes until reopened. Tests cover string/stat/node/close, full and chunked readdir, EOF, and names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/dir_handle.go -->
