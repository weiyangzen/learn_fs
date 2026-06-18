# File Research: sources/local-fs/xfsprogs/libxfs/xfs_dir2_sf.c

## Purpose
Implements XFS shortform directory operations, where small directories are stored inline in the inode data fork. It handles shortform entry sizing, inode/filetype encoding, create/add/lookup/remove/replace, verification, conversion from block form, and conversion between 4-byte and 8-byte inode encodings.

## Main Entry Points
- `xfs_dir2_sf_entsize()` and `xfs_dir2_sf_nextentry()` handle variable-length entry layout.
- `xfs_dir2_sf_get_ino()`, `xfs_dir2_sf_put_ino()`, `xfs_dir2_sf_get_parent_ino()`, and `xfs_dir2_sf_put_parent_ino()` encode/decode parent and child inode numbers.
- `xfs_dir2_sf_get_ftype()` and `xfs_dir2_sf_put_ftype()` manage optional filetype bytes.
- `xfs_dir2_block_sfsize()` and `xfs_dir2_block_to_sf()` convert block directories back into shortform when they fit.
- `xfs_dir2_sf_addname()`, `xfs_dir2_sf_lookup()`, `xfs_dir2_sf_removename()`, and `xfs_dir2_sf_replace()` implement shortform operations.
- `xfs_dir2_sf_verify()` validates inline directory contents.
- `xfs_dir2_sf_toino4()` and `xfs_dir2_sf_toino8()` repack all entries when inode number width changes.

## Internal Mechanics
Shortform directories omit `"."`; they store `".."` as the parent inode in the header. Normal entries carry name length, block-format offset, name, optional filetype, and either a 32-bit or 64-bit inode number. Entries are ordered by their future block-format offsets so conversion to block form remains possible.

Adding a name chooses an easy append path if enough offset space remains at the end, a hard insert path if an interior hole must be used, or converts to block form if inline storage or block-format offset constraints fail. Replacement may force conversion to 8-byte inode storage, or convert to block form if the widened inline data no longer fits.

## Dependencies
Uses inode local-fork allocation helpers, directory data sizing helpers, block-format conversion routines, transaction inode logging, tracepoints, and name comparison helpers.

## Risks and Notes
All mutation paths repack variable-length inline data, so size and pointer recalculation after `xfs_idata_realloc()` is central. The verifier checks entry bounds, increasing offsets, valid inode numbers, i8count consistency, filetype range, and that the directory could fit in block form. Any change to shortform field ordering must also update the get/put and repacking routines.
