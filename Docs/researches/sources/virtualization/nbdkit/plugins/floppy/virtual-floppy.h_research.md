# File Research: sources/virtualization/nbdkit/plugins/floppy/virtual-floppy.h

This header defines the on-disk FAT32 structures and in-memory model for the floppy plugin.

Key definitions:
- Packed MBR/boot-sector, partition-entry, FSInfo, FAT directory-entry, and LFN-entry structs.
- `struct file` stores Unix name, host path, stat metadata, first cluster, and cluster count.
- `struct dir` stores parent index, name, stat metadata, first cluster, children indexes, file indexes, and on-disk directory table.
- `struct virtual_floppy` stores regions, metadata sectors, FAT buffer, file/dir vectors, data/FAT sizing fields, and sector offsets.

Constants:
- `SECTOR_SIZE` is 512.
- `SECTORS_PER_CLUSTER` is 32.
- `CLUSTER_SIZE` is 16 KiB.
- Directory attribute constants mirror FAT directory entry flags.

Integration:
- `floppy.c` owns the global instance and uses `init_virtual_floppy`, `create_virtual_floppy`, and `free_virtual_floppy`.
- `directory-lfn.c` consumes the directory/file vectors and on-disk structs to build directory tables.
- `virtual-floppy.c` fills layout metadata and regions.

Risks and constraints:
- Packed structs are asserted to exact sector/entry sizes at runtime.
- Comments warn cluster sizing is tied to disk layout and maximum supported size.
