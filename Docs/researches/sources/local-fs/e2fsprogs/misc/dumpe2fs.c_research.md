# File Research: sources/local-fs/e2fsprogs/misc/dumpe2fs.c

## Purpose
Implements `dumpe2fs`, which opens an ext2/3/4 filesystem or image and prints superblock, journal, MMP, bad block, bitmap, and block group descriptor information. It also implements `e2mmpstatus` behavior when invoked under that name.

## Main Behaviors
- Parses options `-bfg himxV` and extended `-o superblock=...`, `-o blocksize=...`.
- Resolves device names using `get_devname`.
- Opens filesystems with 64-bit and threaded ext2fs flags.
- Retries open/read operations with `EXT2_FLAG_IGNORE_CSUM_ERRORS`, then reports checksum errors and advises `e2fsck`.
- Can open e2image metadata files with `EXT2_FLAG_IMAGE_FILE`.
- Prints:
  - Superblock via `list_super`.
  - Journal information for external or inline journals.
  - MMP block details.
  - Bad block list.
  - Per-group descriptor locations, bitmap/table locations, free blocks/inodes, checksums, and group flags.
- Machine-readable `-g` output prints colon-separated group metadata.

## Important Functions
- `print_number` / `print_range`: decimal or hex formatting, with 64-bit width handling.
- `print_free`: compresses free bitmap runs into ranges.
- `print_bg_opts`: prints group descriptor flags such as `INODE_UNINIT`, `BLOCK_UNINIT`, and `ITABLE_ZEROED`.
- `list_desc`: core group descriptor reporting routine.
- `list_bad_blocks`: reads bad block inode and prints either dump or summary format.
- `print_inline_journal_information`: opens the journal inode and lists the JBD2 superblock.
- `print_journal_information`: reads external journal superblock.
- `check_mmp`: uses `ext2fs_mmp_start` in read-only mode to determine whether mount is safe.
- `print_mmp_block`: reads and displays MMP metadata fields.
- `parse_extended_opts`: parses `superblock`, `sb`, `blocksize`, and `bs`.

## Dependencies
- `ext2fs`, `e2p`, JBD kernel structures, UUID support.
- `support/devname.h` and `support/plausible.h`.
- Version metadata from `../version.h`.

## Notes and Edge Cases
- `e2mmpstatus` is not a separate implementation here; `main` checks `argv[0]` for `"mmpstatus"` and switches into MMP-check/header-only behavior.
- Group reporting honors bigalloc by switching terminology from blocks to clusters.
- `DUMPE2FS_IGNORE_80COL` changes formatting around bitmap output.
- If checksums fail but forced/ignored paths succeed, the tool still reports the original checksum problem.
