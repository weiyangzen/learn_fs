# File Research: sources/os/linux/linux-stable/fs/netfs/locking.c

Provides inode-level exclusion between buffered and direct I/O for netfs users.

Key behavior:
- Buffered read/write start functions take `i_rwsem` shared but first clear/block outstanding direct I/O when needed.
- Direct I/O start sets `NETFS_ICTX_ODIRECT`, unmaps/waits cached pages, then downgrades to shared locking.
- Buffered writers take write lock first, then downgrade after direct I/O is blocked.
- End helpers release the shared lock.
- Interruptible/killable locking paths return `-ERESTARTSYS` or lower-level wait errors.

Design:
- Multiple buffered operations may run concurrently once direct I/O is excluded.
- Multiple direct I/O operations may run concurrently once buffered I/O is excluded.
