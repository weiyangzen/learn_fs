# File Research: sources/local-fs/reiserfsprogs/fsck/pass2.c

`pass2.c` handles leaves that pass 1 could not insert whole. It reconstructs them item by item.

Key responsibilities:
- Maintains a relocation list mapping old `(dir_id, objectid)` pairs to newly allocated object IDs.
- Inserts uninsertable leaves in two passes:
  - First pass inserts valid stat-data items.
  - Second pass inserts valid non-stat-data items.
- Resolves object-id collisions between directory objects and non-directory file objects by relocating files or directories.
- Inserts or merges stat-data items, preferring newer format and newer modification time where appropriate.
- Inserts directory entries one at a time with `reiserfs_add_entry()`, after checking hash correctness.
- Dispatches regular file/direct/indirect item insertion to `reiserfsck_file_write()`.
- Links relocated files into `/lost+found` later through `link_relocated_files()`.
- Saves pass-2 completion as `TREE_IS_BUILT`; no large state is serialized after this point.

Important exported helpers:
- `objectid_for_relocation()`
- `linked_already()`
- `link_relocated_files()`
- `save_item()`
- `save_and_delete_file_item()`
- `should_relocate()`
- `insert_item_separately()`
- `load_pass_2_result()`
- `pass_2()`

Dependencies and data flow:
- Consumes `fsck_uninsertables(fs)` and `fsck_allocable_bitmap(fs)` from pass 1.
- Uses `proper_id_map(fs)` to allocate relocation object IDs.
- Uses `rewrite_file()`, `reiserfsck_file_write()`, and semantic helpers to keep files/directories distinct when keys collide.
- Produces a built tree and updates `fs->fs_bitmap2` from `fsck_new_bitmap(fs)`.

Notable behavior:
- Stat-data insertion is intentionally first so later file items can be matched to an object.
- Directory stat data causes same-key non-directory items to be moved away; non-directory stat data may be relocated if directory items already occupy the key.
- If no root metadata is found after pass 2, `pass_2()` emits a long diagnostic about possible partition-start shifts or wiped data.
