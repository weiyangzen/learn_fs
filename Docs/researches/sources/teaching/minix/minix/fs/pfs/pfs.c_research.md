# File Research: sources/teaching/minix/minix/fs/pfs/pfs.c

`pfs.c` implements the MINIX Pipe File Server, an in-memory fsdriver service for anonymous pipes and cloned device-like nodes. It uses a fixed table of 512 inodes and a free list; there is no persistent storage and no directory tree.

`pfs_mount` initializes all inode slots, reserves inode number zero by numbering slots from one, places them on the free list, returns an empty root node, and advertises `RES_64BIT`. `pfs_unmount` only warns if in-use inodes remain. `pfs_findnode` validates an inode number and requires the slot to be allocated.

`pfs_newnode` supports FIFO nodes and block/character/socket device nodes. It allocates a `PIPE_BUF` data buffer for FIFOs, initializes metadata and pending timestamp bits, stores device numbers for device-like nodes, and fills the fsdriver node response. `pfs_putnode` expects a single reference, frees any pipe buffer, marks the slot free, and returns it to the free list.

`pfs_read` and `pfs_write` implement linear pipe-buffer I/O. Reads copy from `i_data + i_start`, shrink size, advance the start offset, and mark atime. Writes reject growth beyond `PIPE_BUF`, compact unread data to the beginning when needed, copy input after current data, grow size, and mark ctime/mtime. `pfs_trunc` supports only full pipe truncation. `pfs_stat` materializes lazy timestamps and reports metadata. `pfs_chmod` updates permission bits and times.

The file also includes SEF startup/signal handling, privilege drop to `SERVICE_UID`, the `pfs_table` dispatch table, and `main`, which starts fsdriver processing.
