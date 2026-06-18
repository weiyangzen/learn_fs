# File Research: sources/os/bsd/freebsd-src/sys/sys/_rangeset.h

Range-set structure declaration.

Key elements:
- Defines data duplication/free callback types.
- Defines `struct rangeset` backed by a `pctrie`, callback hooks, callback context, and allocation flags.

Dependencies:
- Includes `sys/_pctrie.h`.

Research notes:
- Generic kernel range-tracking primitive.
- Relevant to VM/VFS/block code that tracks sparse offset or address ranges.
