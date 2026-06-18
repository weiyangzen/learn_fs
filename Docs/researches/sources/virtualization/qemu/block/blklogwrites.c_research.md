# File Research: sources/virtualization/qemu/block/blklogwrites.c

This file implements the `blklogwrites` filter, which logs write, write-zeroes, discard, and flush operations to a separate log file using the Linux `dm-log-writes` disk format.

On-disk format:
- Superblock fields: magic, version, number of entries, sector size.
- Entry fields: sector, number of sectors, flags, data length.
- Flags include flush, FUA, discard, and mark, though the driver emits flush/discard and regular/zero write records.

State:
- `BDRVBlkLogWritesState` tracks the log child, sector size/bits, superblock update interval, current log sector, number of entries, a mutex, active superblock update sequence, and a coroutine queue for serializing superblock updates.

Open behavior:
- Opens the main `file` child and a metadata `log` child.
- Supports `log-append`; if appending, it reads and validates an existing superblock or synthesizes one for an empty log.
- `blk_log_writes_find_cur_log_sector()` scans existing entries to find the append position and validates flags.
- Validates log sector size as power-of-two, large enough for superblock and entry, and below `1 << 24`.
- Initializes mutex and superblock update queue.

I/O behavior:
- Reads pass through unchanged.
- Writes, zero writes, flushes, and discards call `blk_log_writes_co_log()`.
- The driver executes the underlying file operation and log write, then returns a log error preferentially if logging failed, otherwise the underlying file result.
- Log records include an entry header padded to log sector size, followed by data for normal writes or zeroed log space for write-zeroes.
- Discards log only the entry because discard data is not present.

Superblock update:
- The superblock is updated on flush records or every configured interval.
- Only one superblock update runs at a time using `super_update_seq` plus `super_update_queue`.
- Older waiting updates can bail out if a newer sequence already superseded them.
- Superblock update writes a full sector then flushes the log file.

Filesystem/block relevance:
- This is a replay/audit-oriented block filter useful for filesystem consistency testing.
- It captures the write stream needed to reproduce storage mutation order, including discard and flush boundaries.

Potential pitfalls:
- Logging is not atomic with the underlying write; failures are reported but the underlying file may already have changed.
- The mutable log position is reserved under mutex before I/O, so failed log writes can leave gaps or unusable log tails depending on failure mode.
- `log-super-update-interval` cannot be zero.
