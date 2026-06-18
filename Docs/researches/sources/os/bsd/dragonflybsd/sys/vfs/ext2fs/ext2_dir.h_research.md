# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_dir.h

This header defines ext2 on-disk directory entry formats, directory insertion slot tracking, directory checksum tails, file type constants, and record-length alignment helpers.

Key responsibilities:
- Provide old and new ext2 directory entry structures.
- Represent lookup-discovered insertion slots with `struct ext2fs_searchslot`.
- Define metadata-checksum directory tail format.
- Define ext2 directory file type values and maximum link count.
- Provide record length rounding via `EXT2_DIR_REC_LEN`.

Important definitions:
- `struct ext2fs_direct`: Original entry format with 16-bit name length.
- `struct ext2fs_direct_2`: Newer format splitting name length and file type bytes.
- `enum slotstatus` and `struct ext2fs_searchslot`: Tracks whether lookup found no slot, a compactable range, or a directly usable range.
- `struct ext2fs_direct_tail`, `EXT2_FT_DIR_CSUM`, and `EXT2_DIRENT_TAIL`: Directory checksum tail support.
- `EXT2_FT_*`: On-disk file type values.
- `EXT2_DIR_PAD`, `EXT2_DIR_ROUND`, `EXT2_DIR_REC_LEN`: Four-byte directory entry alignment.

Important interactions:
- Used heavily by `ext2_lookup.c`, `ext2_htree.c`, and `ext2_csum.c`.
- File type values are translated to/from DragonFly `dirent` types in lookup/readdir code.

Notable behavior:
- Directory checksum tails masquerade as unused directory entries with a reserved file type.
