# File Research: sources/teaching/os161/kern/include/kern/sfs.h

Defines SFS on-disk format and constants shared with userland tools.

Key constants:
- `SFS_MAGIC`, `SFS_BLOCKSIZE` 512, volume/name sizes.
- Direct/indirect layout: 15 direct blocks, one indirect block, 128 data block pointers per indirect block.
- Superblock, freemap, free dir entry, and root inode locations.
- Freemap sizing macros.
- File types: invalid, file, directory.

On-disk structures:
- `struct sfs_superblock` is exactly one block.
- `struct sfs_dinode` is exactly one block and stores size, type, link count, direct pointers, indirect pointer, and padding.
- `struct sfs_direntry` stores inode number plus fixed-size name.

Relevance:
- Kernel SFS and tools like `mksfs`/`dumpsfs` must agree on this layout.
