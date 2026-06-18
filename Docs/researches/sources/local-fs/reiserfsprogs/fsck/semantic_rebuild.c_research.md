# File Research: sources/local-fs/reiserfsprogs/fsck/semantic_rebuild.c

`semantic_rebuild.c` implements pass 3, the semantic phase of `--rebuild-tree`.

Key responsibilities:
- Provides progress display helpers `print_name()` and `erase_name()` for showing the current traversal path.
- Provides shared stat-data validation/correction helpers used by both rebuild and check:
  - `wrong_st_size()`
  - `wrong_st_blocks()`
  - `wrong_mode()`
  - `wrong_first_direct_byte()`
- Relocates directories when object IDs collide with already reached objects.
- Recursively walks from the root directory, marks reachable items, fixes `.`/`..`, updates link counts, and repairs directory/file stat data.
- Handles regular files via `rebuild_check_regular_file()`, which increments link count, marks reachable file items, validates item sequence, and corrects size/block/mode fields.
- Creates or validates `/lost+found`, including stat data and `.`/`..`, and inserts it into the root directory if needed.
- Links relocated files into `/lost+found`.
- Adds bad-block list entries after semantic rebuild.
- Saves semantic completion as `SEMANTIC_DONE`.

Important exported helpers:
- `print_name()`
- `erase_name()`
- `wrong_st_size()`
- `wrong_st_blocks()`
- `wrong_mode()`
- `wrong_first_direct_byte()`
- `relocate_dir()`
- `rebuild_check_regular_file()`
- `get_object_key()`
- `fix_obviously_wrong_sd_mode()`
- `is_dot()`
- `is_dot_dot()`
- `not_a_directory()`
- `not_a_regfile()`
- `zero_nlink()`
- `modify_item()`
- `load_semantic_result()`
- `pass_3_semantic()`

Dependencies and data flow:
- Consumes the rebuilt tree from pass 2.
- Uses `semantic_id_map(fs)` to detect object-id sharing during traversal.
- Uses `proper_id_map(fs)` for allocation of new object IDs and persistence.
- Sets reachability flags consumed by `pass4.c`.

Notable behavior:
- At the start of rebuild, stat-data link counts have been zeroed and items marked unreachable. Traversal increments link counts and marks reachable items.
- Non-root entries pointing nowhere are removed during rebuild.
- Root `..` pointing to `REISERFS_ROOT_PARENT_OBJECTID` is tolerated.
- Directory and regular-file collisions are handled by relocation and directory-entry key updates.
