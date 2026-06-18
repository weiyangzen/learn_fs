# File Research: sources/local-fs/reiserfsprogs/lib/misc.c

Implements general utilities. Memory allocation wraps each allocation with begin/end sentinels and size metadata so `checkmem()`, `get_mem_size()`, `expandmem()`, and `freemem()` can detect corruption and manage resizing.

Other responsibilities:
- `die()` formats a fatal message and aborts.
- Mount detection searches `/proc/mounts` and mtab, with special handling for root and read-only mtab.
- Progress helpers render percentage marks and throughput estimates.
- `count_blocks()` determines block-device or regular-file size via `BLKGETSIZE64`, `BLKGETSIZE`, or probing offsets.
- Mask helpers build 16/32/64-bit masks.
- `reiserfs_bin_search()` provides generic sorted-array lookup/insertion positioning.
- Sorted block/device list insertion supports rollback bookkeeping.
- DMA helpers query IDE/XT support and drive DMA state/speed where platform ioctls exist.
- `user_confirmed()` reads an exact confirmation string from stdin.
