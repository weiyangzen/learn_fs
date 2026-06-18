# File Research: sources/os/linux/linux/fs/ubifs/io.c

## Purpose

`io.c` implements UBIFS low-level I/O wrappers, node validation/preparation, write-buffer management, and node read/write helpers. It is the boundary between UBIFS metadata semantics and UBI LEB operations, adding UBIFS-specific checks, CRCs, sequence numbers, padding, timers, and read-only failover.

## UBI Wrappers and Read-Only Failover

`ubifs_leb_read()`, `ubifs_leb_write()`, `ubifs_leb_change()`, `ubifs_leb_unmap()`, `ubifs_leb_map()`, and `ubifs_is_mapped()` wrap the corresponding UBI APIs. Write-like operations assert the filesystem is not mounted read-only, return `-EROFS` after an earlier fatal write error, and call `ubifs_ro_mode()` on I/O failure. `ubifs_ro_mode()` sets `ro_error`, disables skipped data CRC checks, marks the VFS superblock read-only, warns, and dumps the stack.

## Node Checking and Preparation

`ubifs_check_node()` validates the common header magic, node type, length range, LEB bounds, and CRC. It may skip data-node CRCs when `no_chk_data_crc` is active, but not during mount/remount recovery or when forced. It records magic, node type, and CRC error counters when stats are present.

`ubifs_pad()` emits either a padding node or padding bytes. `next_sqnum()`, `ubifs_init_node()`, `ubifs_crc_node()`, `ubifs_prepare_node_hmac()`, `ubifs_prepare_node()`, and `ubifs_prep_grp_node()` initialize common headers, assign monotonically increasing sequence numbers, add padding, optionally insert HMACs, and compute CRCs. Grouped node preparation sets `UBIFS_IN_NODE_GROUP` or `UBIFS_LAST_OF_NODE_GROUP`, which journal operations rely on for atomic multi-node updates.

## Write-Buffer Mechanics

UBIFS write-buffers are sized for `max_write_size` but synchronize only the used region rounded up to `min_io_size`. `ubifs_wbuf_sync_nolock()` pads the dirty tail, writes it, advances `wbuf->offs`, recomputes the next buffer size to regain max-write alignment, clears inode tracking, and invokes an optional sync callback for lprops accounting.

`ubifs_wbuf_write_nolock()` is the central buffered write path. It handles small nodes that fit entirely in the buffer, nodes that fill and flush the buffer, unaligned offsets that must be advanced to the next optimal write boundary, direct writes of full max-write units, and residual data left buffered with an hrtimer. It returns `-ENOSPC` if the node cannot fit in the current LEB and produces detailed dumps on unexpected write failures.

`ubifs_bg_wbufs_sync()` is driven by timer state (`need_sync`, `need_wbuf_sync`) and synchronizes only unlocked write-buffers needing flush. It cancels timers after fatal errors to avoid repeated failures. `ubifs_wbuf_seek_nolock()` retargets an empty write-buffer to a new LEB offset.

## Read Paths

`ubifs_write_node_hmac()` and `ubifs_write_node()` write one prepared, min-IO-aligned node directly to media. `ubifs_read_node()` reads from flash, validates type, CRC, and exact length, and reports mapping status on errors. `ubifs_read_node_wbuf()` overlays unwritten bytes from a write-buffer when the requested node overlaps buffered data, preventing stale reads before flush.

## Inode-Scoped Sync Tracking

`ubifs_wbuf_init()` allocates both the data buffer and an inode-number array. `ubifs_wbuf_add_ino_nolock()` records inodes whose nodes are currently buffered. `ubifs_sync_wbufs_by_inode()` scans non-GC heads for a matching inode and synchronizes those write-buffers, supporting fsync-style guarantees without flushing unrelated GC copies.

## Key Invariants

Offsets are 8-byte aligned and write-buffer writes respect `min_io_size` and `max_write_size`. Unexpected write errors move the filesystem to read-only mode. Buffered writes require the caller to hold `wbuf->io_mutex`; internal fields shared with readers use `wbuf->lock`.
