# File Research: sources/os/linux/linux-stable/fs/befs/datastream.h

This header exposes BeFS datastream helpers.

Exports:
- `befs_read_datastream()`
- `befs_fblock2brun()`
- `befs_read_lsymlink()`
- `befs_count_blocks()`
- `BAD_IADDR`

Integration:
- Used by `linuxvfs.c` for file block mapping, long symlinks, and block accounting.
- Used by `btree.c` for B+tree reads.
- Depends on BeFS types from `befs.h`.

Risk notes:
- Callers own returned `buffer_head` lifetimes and must `brelse()` them.
