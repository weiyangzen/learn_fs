# File Research: sources/os/linux/linux-stable/fs/hfs/catalog.c

## Scope

Implements classic HFS catalog B-tree key creation, record/thread creation, lookup-by-CNID, create/delete/move operations, and catalog key comparison.

## APIs And Behavior

- `hfs_cat_build_key()` builds a catalog key from parent CNID and optional name, converting Linux names to Mac names.
- `hfs_cat_create()` creates both the thread record keyed by new CNID and the visible directory/file record keyed by parent/name, with pre-reservation for B-tree splits and rollback of the thread record on failure.
- `hfs_cat_keycmp()` orders records by parent ID then Macintosh lexical order via `hfs_strcmp()`.
- `hfs_cat_find_brec()` resolves a CNID through its thread record, validates thread type/name length, reconstructs the parent/name key, and finds the visible catalog record.
- `hfs_cat_delete()` deletes the visible record, frees resource forks for files, adjusts open readdir positions, removes the thread record when present, updates parent size/mtime, and corrects `next_id`.
- `hfs_cat_move()` implements rename by inserting a destination visible record, removing the source record, then replacing the thread record with one pointing at the new parent/name.

## State And Dependencies

This file updates directory `i_size`, timestamps, catalog B-tree records, MDB counters indirectly through inode deletion paths, and open directory iteration cursors. It depends on B-tree search/mutation, string conversion, extent freeing for resource forks, and `HFS_SB(sb)->next_id`.

## Risks And Invariants

Catalog entries are paired with thread records; create/move/delete must keep the two in sync. `hfs_correct_next_unused_CNID()` scans backward from the leaf tail after deletion to repair the allocator's next CNID, and treats malformed leaf ordering/key lengths as corruption. Readdir position adjustment is protected only against release by `open_dir_lock` and relies on the VFS directory lock for catalog deletion exclusion.
