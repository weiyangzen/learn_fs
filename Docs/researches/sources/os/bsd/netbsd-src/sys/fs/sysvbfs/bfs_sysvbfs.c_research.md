# File Research: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/bfs_sysvbfs.c

This file adapts the abstract BFS core to NetBSD kernel vnode/buffer-cache I/O. It defines `struct bc_io_ops`, which embeds `sector_io_ops` and carries a backing vnode plus credentials. `sysvbfs_bfs_init()` allocates this adapter, installs read/write callbacks, stores the vnode, uses `NOCRED` because the sysvbfs layer performs credential checks, and calls `bfs_init2()` with BFS sector 0 and debugging disabled. `sysvbfs_bfs_fini()` frees the adapter through `bfs->io` and then calls `bfs_fini()`.

The callbacks translate BFS sector operations to buffer-cache block operations. `bc_read_n()` and `bc_write_n()` loop over single-sector callbacks, advancing the caller buffer by `DEV_BSIZE`. `bc_read()` uses `bread()` to read one `DEV_BSIZE` block from the vnode, copies `bp->b_data` into the caller buffer, and releases the buffer with `brelse()`, printing an error on failure. `bc_write()` gets a buffer with `getblk()`, copies the caller data into it, and writes it synchronously with `bwrite()`.

This file deliberately contains only I/O glue. BFS format parsing, allocation, and metadata writeback remain in `bfs.c`; VFS-level authorization and vnode operations are outside this listed file set.
