# File Research: sources/os/linux/linux-stable/fs/hfsplus/catalog.c

## Scope

Implements HFS+ catalog key comparison/building, catalog record/thread construction, permission serialization, CNID lookup, create/delete, rename, and HFSX subfolder count handling.

## APIs And Behavior

- `hfsplus_cat_case_cmp_key()` and `hfsplus_cat_bin_cmp_key()` order catalog keys by parent CNID then casefolded or binary Unicode comparison.
- `hfsplus_cat_build_key()` converts a Linux name to HFS+ Unicode and builds a parent/name key; `hfsplus_cat_build_key_with_cnid()` builds a thread key.
- `hfsplus_cat_set_perms()` serializes mode, uid/gid, immutable/append flags, link count, and device number into HFS+ permission fields.
- `hfsplus_cat_build_record()` creates file/folder catalog records, including HFSX folder count flags, symlink type/creator, hardlink metadata, and hidden-directory visibility flags.
- `hfsplus_find_cat()` resolves a CNID through a thread record, validates thread type/name length, reconstructs the parent/name key, and finds the visible record.
- `hfsplus_create_cat()` inserts thread and visible records with rollback and updates directory size/subfolder counts.
- `hfsplus_delete_cat()` deletes visible and thread records, frees resource forks, adjusts active readdir offsets, updates directory metadata, and deletes all xattrs for deleted files/folders.
- `hfsplus_rename_cat()` inserts a destination record, removes the old visible record, replaces the thread record, and dirties involved catalog inodes.

## State And Dependencies

The file depends on Unicode conversion, B-tree record operations, extents/resource-fork freeing, attributes deletion, hidden directory state, inode dirty flags, and HFSX volume flags.

## Risks And Invariants

Every file/folder should have a thread record; rename/delete must preserve or remove the pair consistently. Hardlinks are represented by catalog proxy records and hidden-directory backing records. HFSX subfolder counts are best-effort and decremented only if nonzero because older implementations may not maintain them.
