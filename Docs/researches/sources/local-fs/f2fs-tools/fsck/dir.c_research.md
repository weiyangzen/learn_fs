# File Research: sources/local-fs/f2fs-tools/fsck/dir.c

## Purpose
Directory and inode creation support for `sload.f2fs` and fsck repair paths. Much of the logic mirrors Linux kernel F2FS directory handling.

## Key functionality
- Directory-entry layout helpers:
  - `make_dentry_ptr` abstracts block dentry vs inline dentry layouts.
  - `room_for_filename` finds consecutive free dentry slots.
  - `find_target_dentry`, `find_in_block`, `find_in_level`, and `f2fs_find_entry` implement hash-directory lookup.
  - `f2fs_lookup` returns inode number for a child name.
- Directory mutation:
  - `f2fs_update_dentry` fills dentry metadata and slot bitmap bits.
  - `f2fs_add_link` adds a child entry, allocating dentry data blocks and updating parent inode depth, size, and link count.
- New inode setup:
  - `make_empty_dir` creates `.` and `..`.
  - `page_symlink` stores symlink target inline or in a warm data block.
  - `set_file_temperature` marks hot/cold files based on superblock extension lists.
  - `init_inode_block` fills inode metadata, footer, inline flags, xattrs, timestamps, name, type, and checksum.
- Inline dentry conversion:
  - `convert_inline_dentry` expands inline directory entries into regular dentry blocks, preserving entries and adding them through normal directory insertion when needed.
- Hardlink cache:
  - Uses libc `tsearch` with `cmp_from_devino`.
  - `f2fs_search_hardlink` tracks source device+inode to F2FS inode mappings for `sload`.
- Creation/path APIs:
  - `f2fs_create`
  - `f2fs_mkdir`
  - `f2fs_symlink`
  - `f2fs_find_path`

## Dependencies
Heavily depends on:
- node helpers from `node.h`
- allocation/write helpers from `segment.c`
- metadata helpers from `fsck.h`
- global configuration `c`
- `f2fs_dentry_hash`, `get_dnode_of_data`, `new_data_block`, `reserve_new_block`, `update_block`, `update_inode`, `update_nat_blkaddr`

## Important behavior
- Directories must convert inline dentries before adding new entries.
- Zoned devices use `update_block` for existing dentry blocks to avoid invalid overwrite patterns.
- Hardlinks reuse the original inode and increment `i_links`; first occurrence records the mapping.

## Research notes
This file is central to repair-time reconnection and image loading. It must preserve F2FS hash-directory placement rules, inline layout rules, and NAT/SIT/summary consistency through helper calls.
