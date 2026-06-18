# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_dir.h

This header defines ext2 on-disk directory entry formats, directory slot tracking, checksum tails, file type constants, and record alignment helpers.

Key responsibilities:
- Define old and new ext2 directory entry structures.
- Represent lookup insertion slot state.
- Define metadata-checksum directory tails.
- Define ext2 file type values and maximum link count.
- Provide record length alignment via `EXT2_DIR_REC_LEN`.

Important definitions:
- `struct ext2fs_direct`: Legacy directory entry with 16-bit name length.
- `struct ext2fs_direct_2`: Directory entry with 8-bit name length and file type.
- `enum slotstatus` and `struct ext2fs_searchslot`: Tracks discovered free/compactable insertion space.
- `struct ext2fs_direct_tail`, `EXT2_FT_DIR_CSUM`, `EXT2_DIRENT_TAIL`.
- `EXT2_FT_*` file type constants.
- `EXT2_DIR_PAD`, `EXT2_DIR_ROUND`, `EXT2_DIR_REC_LEN`.

Important interactions:
- Used by directory lookup/update code, HTree indexing, directory checksum handling, and readdir type translation.

Notable behavior:
- Directory checksum tails masquerade as special unused directory entries at the end of a block.
