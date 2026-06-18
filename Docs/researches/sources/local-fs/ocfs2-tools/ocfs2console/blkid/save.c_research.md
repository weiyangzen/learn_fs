# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/save.c

Serializes an in-memory blkid cache back to disk.

Key functions:
- `save_dev(dev, FILE *file)`
  - Skips non-absolute device names.
  - Writes one XML-like `<device ...>path</device>` line.
  - Includes `DEVNO`, `TIME`, optional `PRI`, and all device tags.
- `blkid_flush_cache(cache)`
  - Skips if no devices or cache not changed.
  - Checks cache file writability.
  - For regular existing files, writes to `filename-XXXXXX` via `mkstemp`.
  - Creates a `.old` backup by link and renames temp file into place.
  - Clears changed flag on successful write.

Dependencies:
- `list_for_each`
- `blkid_struct_dev` and tags from `blkidP.h`

Notable details:
- Does not escape tag names/values or device names when writing, matching the simple parser assumptions.
- Calls `fchmod(fd, 0644)` after `mkstemp`; if `mkstemp` failed, `fd` is invalid but still passed to `fchmod`.
- Returns `1` after successful write, `0` when skipped, negative for parameter error, or errno-like values on open failures.
