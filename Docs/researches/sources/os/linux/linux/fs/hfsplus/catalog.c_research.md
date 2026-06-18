# File Research: sources/os/linux/linux/fs/hfsplus/catalog.c

Purpose: Implements HFS+ catalog key comparison/building, file/folder/thread record construction, lookup by CNID, create/delete, rename, permissions encoding, and HFSX subfolder count maintenance.

Key functions:
- `hfsplus_cat_case_cmp_key()` and `hfsplus_cat_bin_cmp_key()` compare catalog keys by parent then Unicode name with casefold or binary semantics.
- `hfsplus_cat_build_key()` and `hfsplus_cat_build_key_with_cnid()` build regular and thread keys.
- `hfsplus_cat_set_perms()` serializes Linux inode flags, mode, owner, group, device, and nlink into HFS+ permissions.
- `hfsplus_cat_build_record()` initializes folder/file records, including symlink type/creator and hardlink metadata.
- `hfsplus_fill_cat_thread()` creates variable-length file/folder thread records.
- `hfsplus_find_cat()` resolves a CNID thread record then finds the real catalog record.
- `hfsplus_create_cat()` inserts thread and visible records and updates directory valence/subfolder counts.
- `hfsplus_delete_cat()` removes visible and thread records, frees resource forks, adjusts active readdir positions, deletes xattrs, and marks catalog/dir dirty.
- `hfsplus_rename_cat()` inserts the destination record, removes source record, rewrites the thread record, and updates source/destination metadata.

Dependencies and integration:
- Uses HFS+ Unicode conversion/comparison, B-tree search/mutation, extents fork freeing, and attributes deletion.
- Directory and inode operations call these functions for VFS namespace changes.

Risk notes:
- Data fork freeing remains disabled in catalog delete; resource fork freeing is active.
- Hardlink catalog records use hidden directory conventions that must align with `dir.c` link/unlink logic.
