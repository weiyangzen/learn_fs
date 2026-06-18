# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/entry.c

This file implements flashfs's in-memory file tree and extent model.

Key behavior:
- Creates the root entry and an integer map from file numbers to entries.
- Manages directory hash tables, directory child lists, and active directory readers.
- Creates, truncates, removes, walks, stats, chmods, and destroys entries.
- Represents file data as extent lists in two generations/parities.
- Reads file ranges by overlaying extents and zero-filling holes.
- Supports sector renumbering after journal sector copying.

Important details:
- File numbers are assigned monotonically unless restored from journal records.
- Directory removal adjusts active readers so they do not point at removed entries.
- Writes prepend extents and update size/mtime.
- `esum` moves surviving extents between parity lists during summarization.
- `used` tracks live extent payload bytes.

Filesystem relevance:
- Direct: core flashfs vnode/inode-equivalent layer and file data extent map.
