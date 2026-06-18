# File Research: sources/os/linux/linux/fs/ntfs/iomap.h

This header declares the NTFS iomap integration points implemented in `iomap.c`.

Exports:
- `ntfs_write_iomap_ops`
- `ntfs_read_iomap_ops`
- `ntfs_seek_iomap_ops`
- `ntfs_page_mkwrite_iomap_ops`
- `ntfs_dio_iomap_ops`
- `ntfs_writeback_ops`
- `ntfs_iomap_folio_ops`
- `ntfs_dio_zero_range()`

Dependencies:
- Includes Linux `pagemap` and `iomap` APIs.
- Includes NTFS `volume.h` and `inode.h`.

Role in subsystem:
This is the public NTFS-local interface used by file operations, address-space operations, direct I/O paths, and writeback setup to access the iomap operation tables without depending on `iomap.c` internals.
