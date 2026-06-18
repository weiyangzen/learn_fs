# File Research: sources/os/linux/linux/fs/befs/io.c

## Purpose
Low-level BeFS disk I/O helper for reading a block by BeFS inode/block-run address.

## Main Function
- `befs_bread_iaddr()`: validates allocation group, converts `befs_inode_addr` to a logical block number with `iaddr2blockno()`, then reads it with `sb_bread()`.

## Error Handling
- Rejects allocation groups greater than `num_ags`.
- Logs and returns `NULL` on invalid address or failed buffer read.

## Research Notes
This is the bottom of the BeFS read stack. Higher layers map file positions to `befs_inode_addr`, then use this helper to fetch the actual buffer.
