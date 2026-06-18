# File Research: sources/os/linux/linux/fs/adfs/dir_fplus.c

Implements ADFS F+ variable-size “big directory” handling.

Key behavior:
- Computes entry offsets after variable directory name storage and aligned header fields.
- Validates F+ headers:
  - Version bytes must be zero.
  - Start magic must match `BIGDIRSTARTNAME`.
  - Directory size must be nonzero, 2048-aligned, and <= 4 MiB.
  - Name, entry, and names-table areas must fit inside the directory.
- Validates tail magic, sequence, and reserved fields.
- Computes check byte across header, entries, name storage, and tail fields.
- Reads the first block to validate header, then reads the full directory size.
- Handles mismatch between inode directory size and header size as a warning.
- `adfs_fplus_getnext()` reads a big directory entry, then fetches its name from the names area.
- Iteration supports large entry counts via `ctx->pos - 2`.
- Update locates an entry by indirect address and rewrites load/exec/length/indaddr/attr fields.
- Commit increments sequence fields, recomputes check byte, and validates header/tail.

Important interactions:
- Exported through `adfs_fplus_dir_ops`.
- Selected in `super.c` when the disk record has a nonzero format version.
