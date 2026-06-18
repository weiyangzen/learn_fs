# File Research: sources/local-fs/xfsprogs/db/type.c

Maintains the `xfs_db` data type registry and dispatches read/write/fuzz operations by type.

Key responsibilities:
- Registers the `type` command.
- Defines three type tables: non-CRC, CRC, and sparse-inode CRC variants.
- Maps type names to handlers, field tables, buffer ops, CRC offsets, and optional CRC setter callbacks.
- Switches current object type via `set_iocur_type`.
- Provides generic handlers for structured objects, strings, data blocks, and text.

Important behavior:
- CRC tables expose newer types such as rmapbt, refcountbt, realtime rmap/refcount, rtgroup bitmap, and rtgroup summary.
- `handle_struct` supports read, write, and fuzz.
- Text objects are read-only; block/string fuzzing is explicitly unsupported here.
- `type` with no argument prints the current type and supported type names.

Dependencies:
- Pulls together field tables and buffer ops from most `db` metadata modules and libxfs verifier definitions.
- Uses global `cur_typ`, `typtab`, and `iocur_top`.

Notable risks:
- Type enum ordering is asserted against table positions; any enum/table mismatch breaks dispatch.
- Type availability differs across active table variants, so callers must choose the correct table for filesystem features.
