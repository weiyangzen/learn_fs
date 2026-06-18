# File Research: sources/local-fs/ocfs2-tools/sizetest/sizetest.c

## Purpose
Prints offsets and sizes of important OCFS2 on-disk C structures, mainly to verify ABI/layout consistency across ports.

## Main Behavior
- Defines local `offsetof`, `ssizeof`, `START_TYPE`, `SHOW_OFFSET`, and `END_TYPE` helpers for tabular output.
- Prints field offsets and total sizes for:
  - `ocfs2_extent_rec`
  - `ocfs2_chain_rec`
  - `ocfs2_extent_list`
  - `ocfs2_chain_list`
  - `ocfs2_extent_block`
  - `ocfs2_super_block`
  - `ocfs2_local_alloc`
  - `ocfs2_dinode`
  - `ocfs2_dir_entry`
  - `ocfs2_group_desc`
- `main()` calls every printer and exits success.

## Dependencies
- `ocfs2/ocfs2.h` structure definitions.
- Standard output only; no device I/O.

## Notes
This is a diagnostic layout utility. It intentionally computes offsets from null pointer member expressions and prints raw hexadecimal offsets/sizes.
