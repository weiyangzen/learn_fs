# File Research: sources/os/linux/linux/fs/udf/symlink.c

Purpose: UDF symlink page-cache decoding and symlink inode operations.

Key behavior:
- `udf_pc_to_char()` converts UDF `pathComponent` arrays into POSIX symlink text:
  - component type 1/2 can reset to root `/`
  - type 3 emits `../`
  - type 4 emits `./`
  - type 5 decodes a named component using `udf_get_filename()`
- `udf_symlink_filler()` reads inline or block-backed symlink data, rejects symlinks longer than one block, decodes to the folio buffer, and completes folio read.
- `udf_symlink_getattr()` reports `st_size` as decoded link text length rather than encoded UDF byte length.

Integration:
- `udf_symlink()` in `namei.c` creates the encoded path components.
- Exports `udf_symlink_aops` and `udf_symlink_inode_operations`.

Risks and invariants:
- Output buffer reserves a terminating NUL and returns `-ENAMETOOLONG` when decoded text would overflow.
- Malformed component lengths beyond encoded input return `-EIO`.
- Only one-block symlinks are supported.
