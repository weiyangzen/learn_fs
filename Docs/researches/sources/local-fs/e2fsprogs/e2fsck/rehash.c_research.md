# File Research: sources/local-fs/e2fsprogs/e2fsck/rehash.c

This file rebuilds and optionally compresses ext4 indexed directories during pass 3A.

Scheduling API:
- `e2fsck_rehash_dir_later(ctx, ino)` adds a directory inode to `ctx->dirs_to_hash`.
- `e2fsck_dir_will_be_rehashed(ctx, ino)` reports whether a directory will be rebuilt because it is listed or all directories are being compressed.
- `e2fsck_rehash_directories(ctx)` runs pass 3A over either all directories or the scheduled list.

Read/index phase:
- `fill_dir_block()` reads every directory block into a full in-memory buffer and builds a `hash_entry` array for real entries.
- It ignores `.` and `..` when not compressing, tracks the parent from `..`, validates rec_len/name_len constraints, tolerates checksum errors while reading, and handles metadata checksum tail entries.
- It computes hashes via `ext2fs_dirhash2()` unless hashes are already stored in dirents or the directory is being compressed.

Sorting and duplicate handling:
- `hash_cmp()` sorts by major hash, minor hash, and name/inode tie-breakers.
- `name_cmp()` and `name_cf_cmp()` support bytewise and casefold-aware comparisons.
- `duplicate_search_and_fix()` removes exact duplicate dirents pointing to the same inode, drops unrenamable encrypted duplicates, or mutates names using `mutate_name()` until unique.
- After any duplicate fix, entries are resorted.

Output construction:
- `copy_dir_entries()` packs valid entries into output leaf blocks with configured slack for indexed directories and minimum slack for compressed directories.
- It initializes directory entry checksum tails when metadata checksums are enabled.
- `set_root_node()` creates the htree root block with `.` and `..`, chooses SipHash for hash-in-dirent directories, and sets root limits.
- `set_int_node()`, `alloc_blocks()`, and `calculate_tree()` build one- or two-level htree index nodes over the leaf blocks.
- `write_directory()` expands the directory, writes rebuilt blocks, updates `EXT2_INDEX_FL`, sets inode size, and truncates excess blocks with `ext2fs_punch()`.

Main per-directory function:
- `e2fsck_rehash_dir(ctx, ino, pctx)` reads the inode, skips inline-data directories, allocates full-directory memory, indexes entries, falls back to compression if too small for htree, fixes duplicates, builds output blocks/tree, writes the directory, adjusts quota if size shrank, and schedules/checks extent rebuild.

Integration points:
- Uses `problem.c` codes for pass 3A and duplicate directory entries.
- Uses ext2fs block iteration, directory block read/write, dirhash, casefold, htree, allocation, and punch APIs.
- Integrates with quota accounting and extent-tree rebuild/convert paths.

Risk notes:
- The algorithm intentionally uses memory proportional to roughly twice directory size.
- Encrypted duplicate names cannot be safely mutated without a key, so repair can only clear them.
- `outdir->buf` may be reallocated while tree nodes are being built, so offsets are saved and pointers recomputed.
- `lost+found` is special-cased so extra directory blocks are not released during writeback.
