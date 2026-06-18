# File Research: sources/os/linux/linux-stable/fs/ubifs/io.c

## Role

Provides UBIFS low-level I/O wrappers, node validation/preparation, CRC/HMAC handling, padding, sequence numbers, and write-buffer management.

## UBI Wrappers

The file wraps UBI read/write/change/map/unmap calls:

- `ubifs_leb_read()` logs read failures, with special control over `-EBADMSG`.
- `ubifs_leb_write()`, `ubifs_leb_change()`, `ubifs_leb_unmap()`, and `ubifs_leb_map()` reject writes after read-only error state and switch UBIFS to read-only on failures.
- `ubifs_ro_mode()` records fatal write-side errors by setting `c->ro_error`, clearing `no_chk_data_crc`, and marking the superblock read-only.

## Node Validation

`ubifs_check_node()` verifies:

- UBIFS magic.
- Node type range.
- Node length against per-type fixed/min/max ranges.
- LEB bounds.
- CRC, unless data CRC checking is explicitly disabled and the caller does not force it.

It records magic/node/CRC error counters when stats are available and returns `-EUCLEAN` for media-format corruption such as bad magic or CRC.

`ubifs_read_node()` and `ubifs_read_node_wbuf()` read known node types and lengths, including overlap with unwritten write-buffer data.

## Node Preparation

The file initializes on-flash common headers and integrity fields:

- `ubifs_init_node()` assigns magic, length, sequence number, group type, and optional padding.
- `ubifs_crc_node()` calculates node CRC.
- `ubifs_prepare_node_hmac()` optionally inserts HMAC before CRC.
- `ubifs_prepare_node()` is the non-HMAC wrapper.
- `ubifs_prep_grp_node()` prepares grouped atomic journal nodes and marks whether a node is last in the group.

`next_sqnum()` allocates monotonically increasing sequence numbers and forces read-only mode on overflow.

## Padding

`ubifs_pad()` fills min-I/O alignment gaps with either a padding node or padding bytes. This supports scanability of min-I/O padding while allowing small 8-byte alignment gaps between UBIFS nodes to contain arbitrary bytes.

## Write Buffers

Write buffers are max-write-size RAM buffers protected by per-wbuf mutexes and spinlocks. The main operations are:

- `ubifs_wbuf_init()` allocates buffer and inode tracking arrays.
- `ubifs_wbuf_seek_nolock()` targets an empty wbuf to a LEB offset.
- `ubifs_wbuf_write_nolock()` writes nodes through the buffer, flushing full max-write chunks and buffering tails.
- `ubifs_wbuf_sync_nolock()` pads and writes only the used min-I/O-aligned portion, then adjusts future buffer size to regain max-write alignment.
- `ubifs_bg_wbufs_sync()` syncs timer-marked buffers from the background thread.
- `ubifs_sync_wbufs_by_inode()` flushes non-GC buffers containing data for a specific inode.

Timers mark buffers as needing background sync based on `dirty_writeback_interval`.

## Research Notes

This file defines the invariants that higher UBIFS layers rely on: 8-byte node alignment, min-I/O padding, max-write-size optimization, CRC/HMAC sequencing, and fatal write error handling. Journal, GC, log, and lprops debug scans all depend on these helpers.
