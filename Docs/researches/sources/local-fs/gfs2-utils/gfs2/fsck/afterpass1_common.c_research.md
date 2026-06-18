# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/afterpass1_common.c

## Purpose
Provides common post-pass1 deletion and cleanup callbacks for invalid, duplicate, or removed inode metadata, data, directory entries, and extended attributes.

## Main Elements
- Duplicate handling:
  - `find_remove_dup()` removes this inode’s duplicate reference and reports whether references remain.
  - `delete_block_if_notdup()` frees a block only when it is valid, allocated, and no other duplicate refs remain.
- Directory cleanup:
  - `remove_dentry()` deletes a matching dirent during metawalk.
  - `remove_dentry_from_dir()` loads a parent directory and walks it with deletion callbacks.
- Metadata/data callbacks: `delete_metadata()`, `delete_leaf()`, `delete_data()`.
- Extended attribute cleanup:
  - `del_eattr_generic()` clears EA block references and decrements inode block accounting.
  - `delete_eattr_indir()`, `delete_eattr_leaf()`, `delete_eattr_entry()`, `delete_eattr_extentry()` validate and remove bad EA structures/pointers.

## Dependencies And Integration
Used by later fsck passes through `metawalk_fxns`. Integrates duplicate trees, bitmap repair, inode loading, directory walking, logging, and interactive `query()` repair decisions.

## Risk Notes
These routines perform destructive repair by freeing blocks, modifying inode EA pointers, and deleting dirents. Duplicate-reference handling intentionally avoids freeing blocks still referenced elsewhere.
