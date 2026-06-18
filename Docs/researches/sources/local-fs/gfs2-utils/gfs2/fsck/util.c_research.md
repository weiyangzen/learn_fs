# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/util.c

This file provides shared fsck utilities for progress display, interactive prompts, duplicate-block tracking, directory tree tracking, bitmap scans, and cleanup helpers.

Major functions:
- `big_file_comfort()` and `display_progress()` throttle progress output by time and percentage.
- `fsck_getch()`, `generic_interrupt()`, and `fsck_query()` implement interactive yes/no handling, Ctrl-C handling, and global error counters.
- `add_duplicate_ref()`, `find_dup_ref_inode()`, `count_dup_meta_refs()`, `get_ref_type()`, `dup_listent_delete()`, `dup_delete()`, and `delete_all_dups()` maintain duplicate-reference state in rbtrees and lists.
- `dirtree_insert()`, `dirtree_find()`, and `dirtree_delete()` maintain the directory-info rbtree.
- `find_free_blk()` scans resource-group bitmaps for a free block.
- `get_dir_hash()` reads an exhash directory hash table.
- `print_pass_duration()` formats pass runtime.

Dependencies include `libgfs2`, `metawalk`, `logging`, `osi_tree`, and `osi_list` structures through fsck data types.

Risks and notes:
- Several globals are updated or consulted: `errors_found`, `errors_corrected`, `fsck_abort`, `last_fs_block`, progress markers, and duplicate counters.
- `fsck_query()` returns auto-yes/auto-no based on options, so every repair caller inherits noninteractive behavior.
- Duplicate-reference tracking carefully separates invalid-inode references from valid/system references to guide pass1b repair decisions.
