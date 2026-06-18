# File Research: sources/teaching/pintos/src/filesys/file.c

## Purpose
Implements the open-file abstraction over inodes. It provides current-position reads/writes, offset-based reads/writes, seek/tell, length, and per-open-file write denial.

## Main Data Structure
- `struct file`
  - `inode`: backing inode.
  - `pos`: current file offset.
  - `deny_write`: whether this file handle has denied writes on the inode.

## Key Functions
- `file_open(inode)`
  - Takes ownership of an inode and returns a new file wrapper.
  - Closes the inode on failure.
- `file_reopen(file)`
  - Reopens the same inode and returns a separate file wrapper.
- `file_close(file)`
  - Re-enables writes if this handle denied them, closes the inode, and frees the wrapper.
- `file_get_inode(file)`
  - Returns the backing inode.
- `file_read(file, buffer, size)`
  - Reads from current position and advances by bytes read.
- `file_read_at(file, buffer, size, file_ofs)`
  - Reads at an explicit offset without changing `pos`.
- `file_write(file, buffer, size)`
  - Writes at current position and advances by bytes written.
- `file_write_at(file, buffer, size, file_ofs)`
  - Writes at an explicit offset without changing `pos`.
- `file_deny_write(file)` / `file_allow_write(file)`
  - Manage write-denial state on the backing inode.
- `file_length(file)`
  - Returns inode length.
- `file_seek(file, new_pos)` / `file_tell(file)`
  - Manage current position.

## Important Behavior
- File growth is not implemented; writes past EOF are truncated by `inode_write_at()`.
- `file_deny_write()` is idempotent per `struct file`; it increments the inode deny-write counter only once for that handle.
- `file_close()` always calls `file_allow_write()` before closing the inode.
- There is a small comment typo: `file_write()` says it advances by bytes read, but it advances by bytes written.

## Dependencies
- Uses `filesys/inode.h` for storage operations and write-denial counters.
- Uses `threads/malloc.h` for allocation.

## Research Notes
- `struct file` is opaque in `file.h`, making this the sole implementation owner for file-position state.
- No locking is present in this layer.
