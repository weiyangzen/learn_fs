# File Research: sources/local-fs/xfsprogs/db/crc.c

Purpose: implements the `crc` command for v5 XFS metadata structures.

Key behavior:
- `crc_init` registers the command only when the mounted filesystem has CRC metadata enabled.
- `crc` defaults to validation and accepts exactly one of:
  - `-v`: validate/show CRC.
  - `-r`: recalculate CRC by writing the current buffer.
  - `-i`: invalidate CRC by incrementing the CRC field and writing the current buffer.
- Requires a current type with field definitions.
- Finds the first `FLDT_CRC` field recursively with `flist_find_ftyp`, parses the path with `flist_parse`, and prints it with the generic field-list printer.
- For invalidation, walks down to the leaf CRC field, changes the bit value directly, and temporarily swaps write verifier ops to `xfs_dummy_verify` so a bad CRC can be written.
- Recalculation and invalidation require writable expert mode; otherwise the command refuses to write.

Interactions:
- Uses `field.c`/`flist.c` field metadata, `bit.c` bit accessors, current type/buffer state, `write_cur`, and buffer verifier callbacks.
- Depends on per-type CRC fields registered in field tables such as directories, dquots, btrees, inodes, symlinks, and AG metadata.

Risks/notes:
- `-i` intentionally corrupts metadata for testing.
- The printed CRC status depends on current buffer verification state via `iocur_crc_valid`.
