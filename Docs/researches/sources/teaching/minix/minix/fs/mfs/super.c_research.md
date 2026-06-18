# File Research: sources/teaching/minix/minix/fs/mfs/super.c

`super.c` manages superblock I/O and inode/zone bitmap allocation. `alloc_bit` searches either the inode map or zone map from a preferred origin, wraps once, finds the first zero bit, sets it, dirties the bitmap block, and updates libminixfs block-usage accounting for zone allocations. `free_bit` clears a bitmap bit, panics if the bit was already free, dirties the block, and decrements zone usage for zone-map frees.

`get_block_size` returns the current libminixfs filesystem block size and rejects `NO_DEV`.

`rw_super` reads or writes the on-disk superblock stored at byte offset 1024 within block zero. Only fields up to `s_disk_version` are copied to disk; in-memory-only fields after that are zeroed/filled separately. On writes it zeroes the full cache block before copying the on-disk prefix, dirties it, releases it, and flushes all buffers. Read failures are returned cleanly so mounting zero-sized or invalid devices can fail without crashing.

`read_super` validates that the magic is `SUPER_V3`, rejects older V1/V2 magic values, converts fields, rejects multi-block zones (`s_log_zone_size != 0`), validates block size, inode size alignment, layout bounds, and mandatory feature flags, computes `s_firstdatazone` when the legacy field is zero, clamps `s_max_size` to `LONG_MAX`, and initializes search cursors and derived layout values. `write_super` rejects read-only superblocks and delegates to `rw_super`.
