# File Research: sources/os/linux/linux-stable/fs/ocfs2/dir.h

## Summary
Declares the OCFS2 directory manipulation interface and lookup-result structures used by namei, readdir, and directory maintenance code. It abstracts inline, unindexed, and indexed directory details behind one lookup-result container.

## Main Responsibilities
- Define `struct ocfs2_dx_hinfo` for indexed-directory major/minor hash results.
- Define `struct ocfs2_dir_lookup_result`, which carries data-block, dx-root, dx-leaf, dx-entry, hash, and free-list predecessor context.
- Declare lookup, add, delete, update, existence-check, emptiness-check, readdir, initialization, insert-preparation, index truncation, and trailer helper functions.
- Provide `ocfs2_add_entry()` as a dentry-oriented wrapper around `__ocfs2_add_entry()`.

## Key Interfaces
- `ocfs2_find_entry()` fills an `ocfs2_dir_lookup_result`.
- `ocfs2_free_dir_lookup_result()` releases all buffer heads carried by a lookup result.
- `ocfs2_delete_entry()` and `ocfs2_update_entry()` mutate a previously found entry.
- `ocfs2_add_entry()` and `__ocfs2_add_entry()` insert new entries after preparation.
- `ocfs2_prepare_dir_for_insert()` performs space and index preparation before insertion.
- `ocfs2_fill_new_dir()` initializes `"."` and `".."` for new directories.
- `ocfs2_dx_dir_truncate()` removes indexed-directory metadata.
- `ocfs2_dir_trailer_from_size()` locates a directory trailer at the end of an arbitrary block-sized buffer.

## Important Behavior
`ocfs2_dir_lookup_result` can represent multiple layouts. For unindexed directories, `dl_leaf_bh` and `dl_entry` are sufficient. For indexed directories, the caller may also receive `dl_dx_root_bh`, `dl_dx_leaf_bh`, `dl_dx_entry`, `dl_hinfo`, and `dl_prev_leaf_bh` for free-list updates.

## State and Synchronization
The header does not enforce locking but the implementation expects callers of mutating functions to hold VFS directory serialization, OCFS2 cluster locks, and active journal handles as appropriate.

## Cross-File Interactions
`dir.c` implements the functions. Namei and inode code use the interface for create, lookup, link, unlink, rename, rmdir, orphan operations, and directory truncation. The definitions depend on OCFS2 on-disk directory, dx, and allocation structures from the broader filesystem headers.

## Risks
Callers must always release lookup results with `ocfs2_free_dir_lookup_result()` to avoid buffer-head leaks. Mutating helpers rely on the lookup result still matching the prepared directory state; using stale results after dropping locks or after unrelated directory mutation can corrupt data or index state.
