# File Research: sources/local-fs/ocfs2-tools/extras/set_random_bits.c

Read coverage: complete file read, 225 lines.

Purpose: destructive test helper that sets an alternating bit pattern in the global bitmap or another bitmap inode.

Behavior:
- Usage: `set_random_bits [-i <inode_blkno>] <device>`.
- Opens the volume read-write.
- Defaults to the global bitmap system inode if `-i` is not supplied.
- Walks all blocks in the target inode with `ocfs2_block_iterate()`.
- ORs every 32-bit word with `0x55555555`, counts set bits, writes each bitmap block back, then updates the bitmap inode's `i_used` count.

Dependencies: block iteration, raw block I/O, system inode lookup, OCFS2 bitmap inode layout.

Risk notes:
- Intentionally corrupts/changes allocation bitmaps; only suitable for controlled testing.
- It never clears bits, so it only increases apparent allocation.
- Main exits `0` even on many errors.
