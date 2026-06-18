# File Research: sources/os/linux/linux/fs/overlayfs/util.c

## Purpose

`util.c` provides shared overlayfs helper logic for write access, credential override, file-handle capability probing, stack allocation, real path selection, dentry/inode flags, copy-up synchronization, xattr naming, metacopy and fs-verity validation, volatile sync status, in-use locks, nlink/index cleanup, and idmapped attribute copying.

## Main Responsibilities

- Wrap upper mount write access and freeze protection helpers.
- Override credentials with the overlay creator credentials.
- Detect whether underlying filesystems can decode file handles.
- Allocate, copy, free, and release lower stacks and overlay entries.
- Propagate real dentry revalidation flags to overlay dentries.
- Reject unsupported backing dentries.
- Compute overlay path type and select real upper/lower/lowerdata paths.
- Publish lazy lowerdata dentries with correct memory ordering.
- Manage overlay dentry and inode flags.
- Track upperdata state for metacopy/data-copy-up decisions.
- Synchronize copy-up transactions and nlink-sensitive operations.
- Implement private overlay xattr names and xattr fallback behavior.
- Handle impure directories, protection attributes, xwhiteouts, metacopy xattrs, redirects, and fs-verity digests.
- Check volatile sync status and copy real inode attributes into overlay inodes with idmap translation.

## Important Functions

- `ovl_get_write_access()`, `ovl_want_write()`, `ovl_start_write()`, and matching put/drop/end helpers manage upper write access.
- `ovl_override_creds()` applies creator credentials to overlayfs real filesystem operations.
- `ovl_can_decode_fh()` checks exportfs file-handle decode support and detects generic 32-bit inode encoding.
- `ovl_indexdir()`, `ovl_index_all()`, and `ovl_verify_lower()` expose feature predicates.
- `ovl_stack_alloc()`, `ovl_stack_cpy()`, `ovl_stack_put()`, `ovl_stack_free()`, `ovl_alloc_entry()`, and `ovl_free_entry()` manage lower stack storage.
- `ovl_dentry_init_flags()` propagates revalidation requirements from real dentries.
- `ovl_dentry_weird()` rejects backing dentries that overlayfs cannot safely stack.
- `ovl_path_type()`, `ovl_path_upper()`, `ovl_path_lower()`, `ovl_path_lowerdata()`, `ovl_path_real()`, and `ovl_path_realdata()` select backing paths.
- `ovl_dentry_set_lowerdata()` publishes lazy lowerdata after data-layer lookup.
- `ovl_inode_update()` installs an upper dentry after copy-up and hashes the overlay inode if needed.
- `ovl_dir_modified()` copies attributes and increments directory version counters.
- `ovl_path_is_whiteout()` detects both native whiteouts and xattr whiteouts.
- `ovl_path_open()` performs permission checks before opening real paths.
- `ovl_copy_up_start()` and `ovl_copy_up_end()` serialize copy-up and hold upper write access.
- `ovl_init_uuid_xattr()` loads or creates persistent overlay UUID xattrs.
- `ovl_set_impure()` marks upper directories that may contain copied-up entries.
- `ovl_check_protattr()` and `ovl_set_protattr()` translate immutable/append-only protection state through overlay xattrs.
- `ovl_inuse_trylock()`, `ovl_inuse_unlock()`, and `ovl_is_inuse()` manage `I_OVL_INUSE`.
- `ovl_nlink_start()` and `ovl_nlink_end()` synchronize persistent nlink/index updates.
- `ovl_check_metacopy_xattr()` and `ovl_set_metacopy_xattr()` parse and store metacopy metadata.
- `ovl_get_redirect_xattr()` validates redirect xattr syntax.
- `ovl_validate_verity()` and `ovl_get_verity_digest()` compare/store fs-verity digests for metacopy files.
- `ovl_sync_status()` reports whether sync is required or a volatile mount has observed upper writeback errors.
- `ovl_copyattr()` copies mode, ownership, timestamps, and size from the real inode with mount idmap conversion.

## Path And Data Selection

`ovl_path_type()` classifies an overlay dentry as upper-backed, merged, and/or origin-backed. Directory and metacopy cases determine whether reads should use upper, lower metadata, or lowerdata.

`ovl_path_lowerdata()` reads the lowerdata dentry and layer with explicit memory barriers paired with `ovl_dentry_set_lowerdata()`. This supports lazy lowerdata lookup for data-only layers without exposing a dentry before its layer pointer is visible.

## Copy-Up And Upperdata State

`ovl_has_upperdata()` and `ovl_set_upperdata()` use memory barriers so consumers see data-copy effects before the upperdata flag. `ovl_dentry_needs_data_copy_up()` decides whether write/truncate opens require data copy-up. `ovl_already_copied_up()` provides a lockless fast path with documented false-negative tolerance.

`ovl_copy_up_start()` locks the overlay inode and obtains upper write access unless another path already completed copy-up. `ovl_copy_up_end()` releases both.

## Xattrs And Metadata

`ovl_xattr_table` maps internal xattr IDs to either `trusted.overlay.*` or `user.overlay.*` names depending on mount configuration. `ovl_check_setxattr()` records missing xattr support and returns caller-selected fallback errors.

Metacopy helpers treat an empty metacopy xattr as a valid minimal marker and validate non-empty format versions and sizes. Redirect helpers require absolute redirects to have non-empty path components and relative redirects to contain no slashes.

## Index And Nlink Handling

`ovl_need_index()` requests indexing for lower hardlinks, directories under index-all behavior, and NFS-export consistency. `ovl_nlink_start()` may copy up indexed lower objects before whiteout/rename operations so persistent nlink state can be stored. `ovl_cleanup_index()` removes or whiteouts orphan index entries when overlay nlink drops to zero.

## Risk Notes

- Memory ordering around upperdata and lowerdata state is subtle and required for lockless readers.
- `ovl_dentry_weird()` defines what backing dentries are safe; relaxing it could expose automount or custom hash/compare issues.
- Persistent nlink/index cleanup is consistency-critical for hardlinks and NFS export.
- Volatile mounts rely on errseq sampling; missed writeback errors would violate sync semantics.
- Protection attributes intentionally avoid setting immutable/append-only on upper inodes directly.
