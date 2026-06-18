# File Research: sources/local-fs/gfs2-utils/gfs2/tune/super.c

Implements `tunegfs2` superblock read, print, modify, and write operations.

Key functions:
- `read_super`: reads the default block-sized superblock from `GFS2_SB_ADDR << GFS2_BASIC_BLOCK_SHIFT`, checks `GFS2_MAGIC`, and null-terminates lock strings.
- `print_super`: prints volume name, UUID, magic, format, block size/shift, root inode, master inode for GFS2, lock protocol, and lock table.
- `write_super`: writes the in-memory superblock back at `sb_start`.
- `change_uuid`: validates and copies UUID.
- `change_lockproto`: accepts only `lock_dlm` or `lock_nolock`, within `GFS2_LOCKNAME_LEN`.
- `change_locktable`: validates length and, for `lock_dlm`, colon structure and filesystem name length.
- `change_format`: parses and validates filesystem format, disallowing regression.

Dependencies:
- `libgfs2` for constants and endian helpers.
- `libuuid` for UUID parse/unparse.
- `sysexits` for return codes.

Research notes:
- `read_super` allocates `tfs->sb`; ownership persists in the `tunegfs2` struct.
- `change_format` permits forward format changes only within `LGFS2_FS_FORMAT_VALID`.
