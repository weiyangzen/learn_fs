# File Research: sources/local-fs/jfsutils/mkfs/inodes.h

Header for initial inode construction.

Defines:
- `ino_data_type` enum: `inline_data`, `extent_data`, `max_extent_data`, `no_data`.

Declares:
- `init_aggr_inode_table(...)`
- `init_fileset_inode_table(...)`
- `init_fileset_inodes(...)`
- `init_inode(...)`

Filesystem relevance: shared interface for building aggregate/fileset inode tables during formatting.
