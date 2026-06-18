# File Research: sources/virtualization/nbdkit/plugins/floppy/virtual-floppy.c

This file constructs the full FAT32 disk image model used by the floppy plugin.

Key behavior:
- `create_virtual_floppy` scans the input directory tree, builds directory/file lists, creates directory tables, assigns clusters, creates MBR/boot/fsinfo/FAT metadata, and builds final virtual regions.
- `visit` recursively walks directories using `chdir` during `.get_ready`, ignoring non-directory and non-regular files.
- Directories are stored before files in the data region, and both are allocated contiguous cluster chains.
- Optional user-specified `size` reserves extra zero-filled data clusters if larger than content.

Disk layout:
- Sector 0 is MBR.
- Partition starts at sector 2048.
- FAT32 boot sector, FSInfo sector, reserved sectors, backup boot sector, two FAT copies, and data region follow.
- Cluster size is fixed from `SECTOR_SIZE` and `SECTORS_PER_CLUSTER`.

Important implementation details:
- FAT32 cluster numbers are limited to 28 bits.
- MBR partition type is `0x0c` FAT32 LBA.
- Boot sector uses OEM name `MSWIN4.1`, fixed volume ID `0x01020304`, two FATs, root cluster 2.
- Zero-size files occupy no region or FAT cluster.
- Region construction pads FATs and data objects to cluster alignment.

Dependencies:
- Uses `directory-lfn.c` via `create_directory`, `update_directory_first_cluster`, and `pad_string`.
- Uses common helpers: `regions`, `rounding`, `byte-swapping`, cleanup macros, and dynamic vectors.

Risks and edge cases:
- Uses `chdir` recursively, safe only because execution happens before daemonization/threading.
- Symlinks and special files are ignored.
- Host file mutation after image creation can lead to read errors or inconsistent exported data.
- Random/deterministic ordering depends on host `readdir` order.
