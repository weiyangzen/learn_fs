# File Research: sources/os/linux/linux-stable/fs/minix/minix.h

## Purpose

Defines MINIX filesystem private in-memory structures, version constants, internal helper declarations, operation-table declarations, and bitmap-endianness helpers.

## API Surface

- `struct minix_inode_info`: stores V1/V2 pointer arrays, metadata buffer tracking, and embedded VFS inode.
- `struct minix_sb_info`: stores inode/zone counts, bitmap sizes, first data zone, directory sizing, bitmap buffers, raw superblock buffer, mount state, and version.
- Declares inode/block allocation, raw inode access, directory operations, stat/truncate/block-map helpers, fsync, and operation tables.
- `minix_sb()` and `minix_i()` convert generic VFS objects to MINIX-private objects.
- `minix_blocks_needed()` computes bitmap block requirements.
- Bitmap macros select native-endian, big-endian 16-bit indexed, or little-endian bit operations.

## Dependencies

Includes Linux VFS, pagemap, and public MINIX on-disk format definitions. The endian behavior depends on `CONFIG_MINIX_FS_NATIVE_ENDIAN` and `CONFIG_MINIX_FS_BIG_ENDIAN_16BIT_INDEXED`.

## Risks

This header is the contract across all MINIX source files. A mismatch in bitmap bit numbering or inode private layout would corrupt allocation state. The compile-time error for incompatible endian settings protects a known broken configuration.
