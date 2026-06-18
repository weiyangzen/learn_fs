# File Research: sources/os/linux/linux-stable/fs/ntfs/index.h

## Scope

This header declares the public NTFS index interface and the `struct ntfs_index_context` used by lookup, mutation, and traversal code.

## APIs And Data Structures

- `VCN_INDEX_ROOT_PARENT` is the sentinel parent VCN for resident `$INDEX_ROOT`.
- `MAX_PARENT_VCN` caps traversal depth and sizes the parent stack arrays.
- `struct ntfs_index_context` stores:
  - Target index inode/name.
  - Current entry, key/data pointers, and collation rule.
  - Whether the current entry is in root or allocation.
  - Resident root search context or index block buffer.
  - Index allocation inode reference.
  - Parent position and VCN stacks.
  - Block size, VCN size bits, dirty flag, and sync-write flag.
- Declared APIs include:
  - validation: `ntfs_index_entry_inconsistent()`
  - context lifecycle: `ntfs_index_ctx_get()`, `ntfs_index_ctx_put()`, `ntfs_index_ctx_reinit()`
  - lookup/traversal: `ntfs_index_lookup()`, `ntfs_index_walk_down()`, `ntfs_index_next()`
  - mutation: `ntfs_index_entry_mark_dirty()`, `ntfs_index_add_filename()`, `ntfs_index_remove()`, `ntfs_index_rm()`, `ntfs_ie_add()`
  - index allocation access: `ntfs_ia_open()`, `ntfs_icx_ib_sync_write()`

## Dependencies And Invariants

The header depends on NTFS attribute and MFT structures plus VFS types. Callers must release contexts with `ntfs_index_ctx_put()`, and any modifications to index entries must be marked dirty or sync-written before releasing the context.
