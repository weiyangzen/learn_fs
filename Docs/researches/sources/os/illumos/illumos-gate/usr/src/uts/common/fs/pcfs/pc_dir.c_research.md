# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pcfs/pc_dir.c

Directory entry lookup, creation, removal, rename, short-name generation, long-filename entry construction, and start-cluster accessors for PCFS.

Key responsibilities:
- Implements `pc_dirlook()`, `pc_direnter()`, `pc_dirremove()`, and `pc_rename()` as the main directory mutation and lookup layer.
- Handles root-directory special cases for synthetic `.` and `..`, FAT12/FAT16 fixed roots, and FAT32 cluster-backed roots.
- Creates directory entries with `pc_makedirentry()`, including timestamp initialization, readonly/archive attributes, new-directory cluster allocation, and `.`/`..` templates.
- Searches directories with `pc_findentry()` and block-level access through `pc_blkatoff()`.
- Matches both long names and short 8.3 names through `pc_match_long_fn()`, `pc_match_short_fn()`, and `pc_parsename()`.
- Allocates contiguous free directory slots, extending cluster-backed directories as needed in `pc_find_free_space()`.
- Converts UTF-8 names into UTF-16 long filename entries via `pc_name_to_pcdir()` and computes the required number of entries in `direntries_needed()`.
- Generates collision-resistant DOS 8.3 aliases with `generate_short_name()` and `shortname_exists()`.
- Maintains directory-parent correctness on cross-directory rename through `pc_dirfixdotdot()`.
- Provides FAT12/FAT16/FAT32 start-cluster getters and setters.

Dependencies:
- Uses PCFS allocation and node APIs, long-filename helpers from `pc_vnops.c`, Unicode conversion and comparison APIs, buffer cache I/O, vnode event hooks, and PCFS lock/verify discipline.
- Depends on exact `struct pcdir` and `struct pcdir_lfn` on-disk layout.

Notable risks:
- Long filename validity depends on ordinal ordering, checksum agreement with the short entry, UTF conversion success, and prohibited-character filtering.
- Rename removes the old name then creates the new name, preserving cluster, size, timestamps, NT attributes, and FAT32 high cluster fields; failures after removal can mark the filesystem irrecoverable.
- Hidden-directory policy blocks creation and hides matching/reading unless mounted with hidden-file support.
- Directory slot allocation must handle entries that cross block or cluster boundaries.
