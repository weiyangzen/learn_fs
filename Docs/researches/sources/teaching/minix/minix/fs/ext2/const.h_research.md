# File Research: sources/teaching/minix/minix/fs/ext2/const.h

This header defines ext2 server constants, operation codes, inode/block layout values, feature masks, and directory-entry macros.

Major definitions:
- Cache/table sizes: `NR_INODES`, `INODE_HASH_SIZE`, `INODE_HASH_MASK`.
- Directory operation flags: `LOOK_UP`, `ENTER`, `DELETE`, `IS_EMPTY`.
- Inode dirty/time flags: `IN_CLEAN`, `IN_DIRTY`, `ATIME`, `CTIME`, `MTIME`.
- ext2 layout constants: `ROOT_INODE`, `SUPER_BLOCK_BYTES`, `EXT2_NDIR_BLOCKS`, `EXT2_IND_BLOCK`, `EXT2_DIND_BLOCK`, `EXT2_TIND_BLOCK`, `EXT2_N_BLOCKS`.
- Directory record sizing helpers: `DIR_ENTRY_ACTUAL_SIZE`, `DIR_ENTRY_SHRINK`, `DIR_ENTRY_MAX_NAME_LEN`.
- Feature masks: compatible, read-only-compatible, incompatible features, and supported feature sets.
- File type constants for ext2 directory entries.
- Preallocation width: `EXT2_PREALLOC_BLOCKS`.

Role:
- Provides the common semantic contract used by allocation, path lookup, mount feature checks, and block mapping.
- `MAX_FAST_SYMLINK_LENGTH` ties fast symlink capacity to the inode block pointer array.

Notable constraints:
- `EXT2_NDIR_BLOCKS` is hard-coded into `ext2_max_size()` assumptions.
- Only `INCOMPAT_FILETYPE` is supported among incompatible features.
- Supported read-only compatible features are sparse super and large file.
