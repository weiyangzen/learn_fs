# File Research: sources/os/linux/linux-stable/fs/overlayfs/util.c

## Purpose

`util.c` provides shared overlayfs helpers for write access, credential override, file-handle capability probing, lower-stack allocation, path selection, dentry/inode flags, whiteout/xattr checks, copy-up synchronization, nlink/index cleanup, metacopy and fs-verity support, volatile sync state, and inode attribute copying.

## Main Functional Areas

### Write And Credential Helpers

`ovl_get_write_access()`, `ovl_put_write_access()`, `ovl_start_write()`, `ovl_end_write()`, `ovl_want_write()`, and `ovl_drop_write()` wrap upper mount/superblock write access.

`ovl_override_creds()` switches to the overlay creator credentials for underlying filesystem access.

### File Handle And Index Feature Helpers

`ovl_can_decode_fh()` checks whether a filesystem supports exportfs decode and whether it uses generic 32-bit inode file handles.

`ovl_indexdir()`, `ovl_index_all()`, and `ovl_verify_lower()` expose index/NFS feature decisions to lookup and copy-up paths.

### Stack And Entry Helpers

`ovl_stack_alloc()`, `ovl_stack_cpy()`, `ovl_stack_put()`, `ovl_stack_free()`, `ovl_alloc_entry()`, and `ovl_free_entry()` manage lower path arrays and references.

### Dentry And Path Helpers

`ovl_path_type()` classifies an overlay dentry as upper, merge, and/or origin. `ovl_path_upper()`, `ovl_path_lower()`, `ovl_path_lowerdata()`, `ovl_path_real()`, and `ovl_path_realdata()` choose the real backing path.

`ovl_dentry_upper()`, `ovl_dentry_lower()`, `ovl_dentry_lowerdata()`, `ovl_dentry_real()`, and inode equivalents expose upper/lower/real backing objects.

`ovl_dentry_set_lowerdata()` installs lazily resolved lowerdata with memory barriers so readers see layer and dentry consistently.

### Flags And Cache State

The file implements dentry flags for opacity, xwhiteouts, and upper alias state, and inode flags for upperdata, impure dirs, index, verity digest state, and related features.

`ovl_dir_modified()` copies attributes and increments directory version when needed. `ovl_inode_version_get()` supports readdir cache invalidation.

### Whiteout, Xattr, UUID, And Protattr Helpers

`ovl_is_whiteout()` and `ovl_path_is_whiteout()` detect device whiteouts and xattr whiteouts.

`ovl_init_uuid_xattr()` loads or creates the persistent overlay UUID xattr when configured, with fallback to `uuid=null`.

`ovl_xattr_table` maps overlay-private xattr IDs to trusted or user namespaces.

`ovl_check_setxattr()` centralizes xattr feature fallback behavior.

`ovl_set_impure()` marks upper dirs that may contain non-pure entries.

`ovl_check_protattr()` and `ovl_set_protattr()` preserve append/immutable semantics through `overlay.protattr` instead of applying those flags directly to upper inodes during copy-up.

### Copy-Up And Nlink Synchronization

`ovl_already_copied_up()` and locked variant check whether copy-up/data copy-up is still needed.

`ovl_copy_up_start()` locks the overlay inode and takes upper write access unless the object is already copied up. `ovl_copy_up_end()` releases both.

`ovl_need_index()` decides whether copy-up should create/use an index entry.

`ovl_nlink_start()` and `ovl_nlink_end()` synchronize link/unlink/rename operations with copy-up and persistent union nlink accounting. `ovl_cleanup_index()` removes or whiteouts orphaned index entries when overlay nlink reaches zero.

### Metacopy And Verity

`ovl_check_metacopy_xattr()` reads and validates metacopy xattrs, accepting empty xattrs as a valid minimal metacopy marker.

`ovl_set_metacopy_xattr()` writes metacopy metadata, optimizing empty digest/flag state to a zero-length xattr.

`ovl_is_metacopy_dentry()` identifies metadata-only copy-up files.

`ovl_get_redirect_xattr()` validates redirect xattrs, allowing absolute redirect paths with sane components and relative redirects without slashes.

`ovl_ensure_verity_loaded()`, `ovl_validate_verity()`, and `ovl_get_verity_digest()` integrate fs-verity digest validation for metacopy lowerdata.

### Sync And Attribute Copying

`ovl_sync_status()` returns whether sync should proceed, be skipped for clean volatile mounts, or fail due to upper writeback errors.

`ovl_copyattr()` mirrors ownership, mode, times, and size from the selected real inode into the overlay inode, applying the real mount idmap.

## Risk Notes

- Memory barriers around `OVL_UPPERDATA`, upper dentry publication, and lowerdata publication are important for lockless readers.
- `ovl_get_redirect_xattr()` is security-sensitive because redirects influence lower path traversal.
- Index cleanup manipulates persistent identity state and must stay synchronized with copy-up/nlink updates.
- `ovl_copyattr()` must remain idmap-aware to avoid incorrect ownership reporting.
