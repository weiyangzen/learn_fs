# File Research: sources/os/linux/linux-stable/fs/befs/io.c

This file provides the lowest BeFS disk-read helper.

Export:
- `befs_bread_iaddr()` converts a BeFS inode/block-run address to a linear block number and reads it with `sb_bread()`.

Flow:
- Logs the allocation group/start/len.
- Rejects allocation groups greater than `num_ags`.
- Converts through `iaddr2blockno()`.
- Calls `sb_bread()`.
- Returns `NULL` on invalid allocation group or read failure.

Integration:
- `datastream.c` uses it in `befs_read_datastream()` after logical-to-run mapping.
- Depends on `BEFS_SB()` geometry and address helpers.

Risk notes:
- The allocation-group check uses `>` rather than `>=`, so an allocation group equal to `num_ags` may pass even though groups are commonly zero-indexed.
- It does not validate `start`, `len`, or final block number against total block count.
