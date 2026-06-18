# File Research: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/bfs.h

This header defines the System V BFS on-disk structures and the in-kernel/standalone core API. The documented layout is one 512-byte superblock sector, followed by 64-byte inode records up to `data_start_byte`, then the data block area through `data_end_byte`.

Constants define BFS parameters: `BFS_SECTOR` zero offset, magic `0x1badface`, 14-byte maximum filename, root inode number 2, 512-byte block size, and block shift 9. Packed on-disk structures include `bfs_super_block_header` (magic and data byte boundaries), `bfs_compaction`, `bfs_fileattr` (type, mode, uid/gid, nlink, timestamps), `bfs_inode` (number, start/end sectors, EOF byte offset, attributes), `bfs_super_block` (header, compaction fields, fsname, volume), and 16-byte `bfs_dirent` entries.

Under `_KERNEL` or `_STANDALONE`, it defines the in-memory `struct bfs`, which caches the superblock image, data range, inode table, root directory entries, root inode, sector I/O ops, and debug flag. `struct sector_io_ops` abstracts single-sector and multi-sector read/write functions. The declared API covers initialization/finalization, file read/write/create/delete/rename/lookup/size, debug dump, sysvbfs vnode-backed initialization/finalization, inode/dirent lookup/delete/allocation, and attribute updates.

The header is shared by the core BFS logic (`bfs.c`) and NetBSD sysvbfs wrapper (`bfs_sysvbfs.c`), and it is exported by the sysvbfs Makefile.
