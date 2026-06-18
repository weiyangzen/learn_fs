# File Research: sources/os/linux/linux/fs/netfs/locking.c

Implements serialization between buffered and direct I/O for netfs inodes.

Important exported APIs:
- `netfs_start_io_read()` / `netfs_end_io_read()`.
- `netfs_start_io_write()` / `netfs_end_io_write()`.
- `netfs_start_io_direct()` / `netfs_end_io_direct()`.

Concurrency model:
- Uses `inode->i_rwsem`.
- Uses `NETFS_ICTX_ODIRECT` to indicate direct I/O mode.
- Buffered reads take shared lock if no direct I/O mode is active.
- Buffered writes take write lock, clear/direct-drain O_DIRECT mode, then downgrade.
- Direct I/O takes shared lock if direct mode already active; otherwise takes write lock to block buffered I/O, flush/wait pagecache, then downgrades.

Important behavior:
- `netfs_block_o_direct()` clears direct mode and waits for outstanding DIO.
- `netfs_block_buffered()` sets direct mode, unmaps pagecache, and waits for writeback.
- Interruptible/killable lock acquisition maps to `-ERESTARTSYS`.
