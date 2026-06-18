# File Research: sources/os/linux/linux/fs/ntfs3/ntfs_fs.h

## Role

Central private header for the NTFS3 driver. It defines in-memory superblock/inode/run/index state and declares the cross-file API surface for attributes, records, directories, indexes, bitmaps, security, xattrs, compression, logging, and mount helpers.

## Major Contents

- NTFS3-specific error codes:
  - `E_NTFS_FIXUP`, `E_NTFS_NONRESIDENT`, `E_NTFS_NOTALIGNED`, `E_NTFS_CORRUPT`.
- Mount and runtime flags:
  - Superblock flags include discard shutdown, log replay, MFT mirror update, and journal-replay-needed states.
  - Inode flags include external compression format bits, deduplication, EA presence, directory/resident state, and parent-update requirements.
- Mount options:
  - `struct ntfs_mount_options` stores NLS, uid/gid, masks, ACL/name/display/hidden/sparse/prealloc/nocase/delalloc settings.
- Core in-memory structures:
  - `struct runs_tree`: array-backed VCN-to-LCN run map.
  - `struct wnd_bitmap`: free-space bitmap window/tree state.
  - `struct ntfs_index`: per-index runlists, locking, and block geometry.
  - `struct ntfs_sb_info`: NTFS3 superblock state, including cluster geometry, MFT state, volume info, security/reparse/object-id indexes, compression contexts, options, and procfs entry.
  - `struct mft_inode`: one loaded MFT record with buffers.
  - `struct ntfs_inode`: Linux inode extension, including MFT record tree, resident/file/dir union, attribute list, valid size, flags, and locking.
  - `struct ntfs_fnd`: index-search path state.
- Declarations:
  - Attribute manipulation from `attrib.c`.
  - Attribute-list handling from `attrlist.c`.
  - Directory/name conversion/search.
  - File operations, inode operations, MFT record operations.
  - Runlist operations from `run.c`.
  - Bitmap, superblock, security, reparse, objid, index, xattr, ACL, and compression functions.
- Inline helpers:
  - Run initialization/free/close.
  - NTFS timestamp conversion.
  - Superblock and inode container helpers.
  - Delayed-allocation counters.
  - Cluster/block alignment conversions.
  - Inode state predicates for compressed/sparse/dedup/encrypted/resident.
  - Buffer release and lock helpers.

## Important Invariants

- `struct ntfs_inode` embeds `struct inode` as `vfs_inode`; `ntfs_i()` is the canonical container conversion.
- NTFS inodes may span multiple MFT records; `mi_tree` and attribute lists represent overflow/subrecord state.
- File and directory state share a union, so callers must honor inode kind flags before accessing `ni->dir` or `ni->file`.
- Runlists are protected by `run_lock` in paths that may load or mutate mappings concurrently.
- MFT, security, reparse, and object-id metadata have nested lock classes to satisfy lockdep ordering.
- Delayed allocation counters are atomic and adapt to 32-bit vs 64-bit cluster builds.

## Dependencies

- Pulls in most kernel filesystem, buffer, page, rwsem, mutex, rbtree, and ID-mapping APIs.
- Depends on `ntfs.h` for on-disk format definitions.
- Acts as the compile-time coupling point for the NTFS3 implementation files.

## Notes For Future Work

- The header is broad and monolithic by design; changes here have large blast radius.
- `runs_tree` still has a TODO to use an rb-tree instead of an array. `run.c` also comments on array/memmove costs.
- Any new operation should respect the existing lock nesting helpers and avoid bypassing `ni_lock`, `run_lock`, and bitmap locks.
