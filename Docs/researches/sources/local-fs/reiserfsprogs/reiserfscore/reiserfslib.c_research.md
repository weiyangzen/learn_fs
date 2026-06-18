# File Research: sources/local-fs/reiserfsprogs/reiserfscore/reiserfslib.c

Core library implementation for opening, creating, searching, mutating, and iterating ReiserFS filesystems from userspace tools. It owns global canonical keys for root, parent root, lost+found, and bad-block pseudo-files, and initializes root key constants through `make_const_keys()`.

Major responsibilities:
- Filesystem lifecycle: `reiserfs_open()`, `reiserfs_create()`, `reiserfs_reopen()`, `reiserfs_flush()`, `reiserfs_free()`, and `reiserfs_close()`.
- Superblock validation/creation: probes ReiserFS superblock at the old/new 4 KiB locations, validates block size, derives format/hash function, creates format 3.5/3.6 superblocks, and initializes mount/check metadata.
- Tree searching: `reiserfs_search_by_key_3()`, `reiserfs_search_by_key_4()`, `reiserfs_search_by_position()`, `reiserfs_search_by_entry_key()`, `uget_lkey()`, `uget_rkey()`, and `reiserfs_next_key()`.
- Tree mutation wrappers: `init_tb_struct()`, `reiserfs_remove_entry()`, `reiserfs_paste_into_item()`, and `reiserfs_insert_item()` delegate balancing to `fix_nodes()`/`do_balance()`.
- Directory operations: hash generation, entry lookup, insertion, root directory/stat-data creation, and maintenance of `"."`/`".."`.
- Bad-block support: builds bad-block bitmaps from files, iterates bad-block indirect items, removes/replaces bad-block items, and writes bad-block block pointers back into the tree.
- File and directory iterators: `reiserfs_iterate_file_data()` walks direct/indirect items for one file; `reiserfs_iterate_dir()` walks directory entries excluding dot entries.

Important implementation details:
- `is_block_count_correct()` ensures reserved area, superblock, root, and journal fit within first bitmap coverage and filesystem size.
- `reiserfs_search_by_key_x()` descends from the root block using `reiserfs_bin_search()`, with 3-field or 4-field key comparison.
- Directory lookup handles hash collisions by scanning generation counters embedded in directory offsets.
- `make_entry()` constructs one `reiserfs_de_head` plus rounded name payload and marks entries visible.
- `create_dir_sd()` creates old/new stat-data according to filesystem format and uses caller uid/gid for non-root invocations.
- `can_we_format_it()` checks mounted state, block-device type, and whole-disk device patterns before journal/filesystem formatting operations.

Dependencies and interactions:
- Relies heavily on `includes.h`/`reiserfs_lib.h` macros for endian-safe superblock, item-head, directory-entry, key, bitmap, and journal access.
- Depends on buffer cache helpers (`bread`, `getblk`, `bwrite`, `brelse`, dirty/uptodate flags), tree balancing (`fix_nodes`, `do_balance`), journal helpers, bitmap helpers, and misc device checks.
- Used by resize, tune, fsck, mkfs, and debug tools as shared core filesystem manipulation code.

Risks and notes:
- Many failures abort through `die()`/`reiserfs_panic()`, which is normal for these low-level tools but makes partial recovery caller-hostile.
- `reiserfs_close()` calls `reiserfs_free(fs)` before `fsync(fs->fs_dev)`, which reads through `fs` after it has been freed.
- Several functions assume path state remains valid across low-level tree operations and panic on structural inconsistency.
- Directory and file iteration are format-aware but mostly trust item bodies after key/type checks; corrupt images can drive warning/error paths.
