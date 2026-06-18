# File Research: sources/os/linux/linux/fs/hfs/catalog.c

Purpose: Implements classic HFS catalog B-tree key construction, comparison, create/delete/rename operations, and CNID thread lookup.

Key functions:
- `hfs_cat_build_key()` builds catalog keys from parent CNID and Mac-encoded name, or a thread lookup key when name is `NULL`.
- `hfs_cat_build_record()` initializes file or directory catalog records.
- `hfs_cat_build_thread()` creates file/folder thread records mapping CNID back to parent/name.
- `hfs_cat_keycmp()` sorts catalog keys by parent ID then Macintosh lexical filename order.
- `hfs_cat_find_brec()` resolves a CNID thread record and then finds the actual catalog record.
- `hfs_cat_create()` inserts thread and visible catalog records atomically enough to roll back the thread on later failure.
- `hfs_cat_delete()` removes the visible record, optional thread record, resource fork blocks, and updates open readdir positions.
- `hfs_cat_move()` implements rename by inserting the new record, removing the old record, and rewriting the thread record.

Dependencies and integration:
- Uses `hfs_asc2mac()`, `hfs_mac2asc()`, `hfs_strcmp()`, B-tree search/mutation APIs, and inode dirty marking.
- Coordinates directory `i_size` as valence plus `.`/`..` convention used by `dir.c`.
- Maintains `next_id` recovery via `hfs_correct_next_unused_CNID()` after deletion.

Risk notes:
- Data fork freeing is compiled out in delete paths; resource fork freeing remains active.
- Rename/create operations depend on prior `hfs_bmap_reserve()` to avoid mid-operation ENOSPC.
- CNID count overflow and corrupt catalog ordering are explicitly guarded in newer code paths.
