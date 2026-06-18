# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/undo_io.c

## Purpose
Implements the libext2fs undo I/O manager. It wraps a backing I/O manager and records original filesystem data into an `e2undo` file before destructive writes, discards, zeroouts, or byte writes modify the target.

## Data Model
- Undo files begin with an `E2UNDO02` header, a stored superblock copy, and key/data block chunks.
- `struct undo_key` maps filesystem block positions to saved data extents and stores per-block CRCs.
- `struct undo_private_data` tracks the real backing channel, undo-file channel, current key block, next undo block, filesystem offset, block bitmap of already-saved regions, and checksummed header state.

## Main Behavior
- `undo_write_tdb()` is the core pre-write hook: it calculates affected undo-sized blocks, skips blocks already captured, reads original data from the backing device, writes it to the undo file, and appends/extends key records.
- `write_undo_indexes()` writes pending key blocks, captures the current superblock with its magic inverted, updates header metadata, and flushes when requested.
- `try_reopen_undo_file()` validates an existing undo file by magic, header CRC, block-size bounds, feature flags, key-block CRCs, and target superblock match, then reconstructs the written-block map to resume appending.
- `undo_close()` marks the undo file finished unless `UNDO_IO_SIMULATE_UNFINISHED` is set.

## Integration
Exports `undo_io_manager` and setup helpers for selecting the backing manager and undo file name. It forwards normal reads, flushes, readahead, stats, and options to the backing channel while intercepting all write-like operations.

## Risks / Notes
- The file is deliberately single-threaded; `undo_open()` clears `IO_FLAG_THREADS`.
- Undo correctness depends on capturing each affected undo block before the first mutation and on superblock/CRC validation preventing cross-filesystem replay.
- Offset support is propagated to the backing manager and recorded as an undo compatible feature.
