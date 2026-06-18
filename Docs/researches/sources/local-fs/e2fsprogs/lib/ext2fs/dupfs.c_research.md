# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/dupfs.c

Implements `ext2fs_dup_handle`, which duplicates an `ext2_filsys` handle while deep-copying owned filesystem metadata and sharing reference-counted IO/cache state.

Duplication behavior:
- Allocates a new `struct_ext2_filsys` and shallow-copies the source.
- Clears pointers that must be independently allocated.
- Bumps IO channel reference count.
- Increments inode cache refcount when present.
- Deep-copies device name, superblock, original superblock, group descriptors, inode bitmap, block bitmap, badblocks list, dblist, MMP buffers, and MMP comparison buffer.
- Duplicates `mmp_fd` with `dup` when present.

Error handling:
- On any allocation/copy failure, calls `ext2fs_free` on the partially built handle and returns the error.
- Returns `EXT2_ET_MMP_OPEN_DIRECT` if duplicating the MMP file descriptor fails.

Implementation notes:
- The duplicate shares the same `io_channel` after bumping its count.
- `mmp_fd` is reset to `-1` before optional duplication so cleanup can distinguish ownership.
