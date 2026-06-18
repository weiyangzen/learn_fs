# File Research: sources/local-fs/gfs2-utils/gfs2/tune/tunegfs2.h

Shared header for `tunegfs2`.

Defines `struct tunegfs2`, carrying:
- Device name, fd, superblock offset, and `struct gfs2_sb *sb`
- Pending string values for UUID, label, table, proto, mount options, format
- Boolean option flags for list, label, UUID, proto, table, and format

Exports:
- `print_super`
- `read_super`
- `write_super`
- `change_uuid`
- `change_lockproto`
- `change_locktable`
- `change_format`

Research notes:
- The API is intentionally stateful around a single mutable `struct tunegfs2`.
