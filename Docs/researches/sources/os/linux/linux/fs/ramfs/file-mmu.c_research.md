# File Research: sources/os/linux/linux/fs/ramfs/file-mmu.c

MMU-enabled ramfs file operation definitions.

Key responsibilities:
- Provides `ramfs_mmu_get_unmapped_area()`, delegating to `mm_get_unmapped_area()`.
- Defines `ramfs_file_operations`:
  - generic read/write iterators,
  - generic mmap preparation,
  - noop fsync,
  - splice read/write,
  - generic llseek,
  - MMU unmapped-area lookup.
- Defines `ramfs_file_inode_operations`:
  - `simple_setattr`,
  - `simple_getattr`.

Important behavior:
- ramfs relies on the VFS page cache rather than private on-disk or in-memory file data structures.
- The file is intentionally minimal and serves as a simple read-write filesystem example.

Research notes:
- NOMMU behavior is separated into `file-nommu.c`; only one implementation is linked by the Makefile.
