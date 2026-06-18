# File Research: sources/local-fs/reiserfsprogs/fsck/semantic_check.c

`semantic_check.c` implements the semantic pass used by `--check` and `--fix-fixable`.

Key responsibilities:
- Recursively walks the directory tree from `root_dir_key`.
- Detects directory loops with a linked list of short keys representing the current traversal path.
- Validates regular files through `are_file_items_correct()` and shared stat-data validators.
- Checks and optionally fixes stat-data fields:
  - mode
  - size
  - block count
  - old-format first-direct-byte metadata
- Checks directory structure:
  - stat data exists
  - `.` and `..` exist and point correctly
  - directory entries are properly hashed
  - new-format entry lengths are aligned
  - names point to existing stat data
  - directory size and block count match entries
- Checks safe links under dirid `-1`, including invalid safe links and truncate links.
- In `FSCK_FIX_FIXABLE`, removes bad entries, adds/fixes `.`/`..`, fixes stat data, updates bitmaps, and applies bad-block list changes.
- In check-only mode, counts fixable/fatal corruptions without mutating most structures.

Important exported helper:
- `semantic_check()`

Important internal helpers:
- `check_path_key()`, `add_path_key()`, `del_path_key()`
- `check_check_regular_file()`
- `get_next_directory_item()`
- `check_semantic_pass()`
- `check_safe_links()`

Dependencies and data flow:
- Uses shared validators from `semantic_rebuild.c` and `ufile.c`: `wrong_mode()`, `wrong_st_blocks()`, `wrong_st_size()`, `wrong_first_direct_byte()`, `get_object_key()`, `print_name()`, `erase_name()`.
- Uses global `trunc_links` to avoid reporting wrong file size for files with valid truncate safe links.
- In fixable mode, initializes `fsck_new_bitmap(fs)` and `fsck_allocable_bitmap(fs)` from the current bitmap so repair operations can allocate/deallocate safely.

Notable behavior:
- Semantic checking is skipped if earlier structural tree checks found bad nodes or fatal corruptions.
- Directory hard links are treated as corruption except for valid `..` traversal.
- Some relocation logic is compiled out for fix-fixable because file rewrite can be too invasive for that mode.
