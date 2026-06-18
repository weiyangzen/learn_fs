# File Research: sources/windows/winbtrfs/src/scrub.c

## Purpose

`scrub.c` implements WinBtrfs scrub support: a privileged, background consistency scan that reads allocated extents from every writable chunk, verifies checksums or tree block headers, records detailed scrub errors, and repairs recoverable corruption by rewriting good mirrored or parity-derived data. It handles simple/duplicate/RAID1-like profiles, RAID0, RAID10, RAID5, and RAID6, then exposes start/query/pause/resume/stop control entry points.

## Core Data Structures

- `SCRUB_UNIT` limits non-parity data scrub work units to 1 MiB.
- `scrub_context_stripe` tracks one physical stripe read: IRP, device-relative start, byte length, buffer, IO status, checksum-error flag, and computed bad checksums.
- `scrub_context` groups multiple stripe reads with a completion event and an interlocked `stripes_left` counter.
- `path_part` is used while reconstructing a human-readable filename for a damaged data extent.
- `scrub_context_raid56_stripe` tracks RAID5/6 stripe buffers, missing/rewrite state, per-sector error bitmap, and IRP state.
- `scrub_context_raid56` holds RAID5/6 run-wide bitmaps for allocated sectors, checksum-covered sectors, tree sectors, loaded checksum bytes, parity scratch buffers, and stripe read state.

## Error Logging

- `log_file_checksum_error()` maps a data extent reference back to a path by walking inode refs, inode extrefs, and root backrefs across subvolumes. It emits a UTF-16 filename into a variable-length `scrub_error` and appends it under `Vcb->scrub.stats_lock`.
- `log_file_checksum_error_shared()` reads a shared leaf and logs any `TYPE_EXTENT_DATA` items pointing at the corrupt physical extent.
- `log_tree_checksum_error()` records metadata errors with root, level, and first key context.
- `log_tree_checksum_error_shared()` reads a parent tree block and logs the child reference that matches the corrupt address.
- `log_unrecoverable_error()` looks up the extent item or metadata item for a physical address, parses inline and keyed extent references, and expands them into file or tree errors. It also follows separate reference items if the inline reference count did not cover the extent refcount.
- `log_error()` is the common front door. Recoverable errors are recorded directly; unrecoverable errors are expanded through extent-reference lookup.

## Mirrored, RAID0, and RAID10 Scrub Flow

- `scrub_read_completion()` stores IRP status, decrements the shared outstanding-read counter, and signals the context event when all reads finish.
- `scrub_extent()` computes per-device physical ranges for the target logical extent, allocates buffers and IRPs, supports buffered/direct/neither IO paths, waits for all stripe reads, accounts `Vcb->scrub.data_scrubbed`, then dispatches by profile:
  - `BLOCK_FLAG_DUPLICATE` for single, duplicate, RAID1, RAID1C3, RAID1C4, and fallback single-like handling.
  - `BLOCK_FLAG_RAID0`.
  - `BLOCK_FLAG_RAID10`.
- `scrub_extent_dup()` verifies mirrored copies. For data, it checks sector checksums against the extent csum array; for metadata, it checks tree checksums and logical addresses. If a good mirror exists, it logs recoverable errors and overwrites bad writable copies. If every mirror has errors, it falls back to sector/tree-block comparison and recovers any sector with a good copy from another mirror.
- `scrub_extent_raid0()` validates each sector or tree block on the one stripe that owns it. RAID0 has no redundancy, so failures are logged as unrecoverable.
- `scrub_extent_raid10()` treats each RAID0-positioned stripe group as a mirror set. It first tries to identify a good sub-stripe, then repairs bad mirror members. If all sub-stripes in a set are bad, it computes per-sector or per-tree-block checksums and recovers sectors when any sibling matches expected data.
- `scrub_data_extent()` uses a bitmap where clear bits represent sectors with checksums and calls `scrub_extent()` only for checksum-covered runs, splitting long runs into `SCRUB_UNIT` chunks.

## RAID5 and RAID6 Scrub Flow

- `scrub_read_completion_raid56()` mirrors the non-parity completion routine for RAID5/6 stripe reads.
- `scrub_chunk_raid56()` walks extent items in bounded batches, maps logical extents to full stripe numbers, and calls `scrub_chunk_raid56_stripe_run()` for contiguous stripe runs. It caps each batch at 64 extents or 128 MiB of logical data.
- `scrub_chunk_raid56_stripe_run()` builds allocation, tree, and checksum bitmaps for a full stripe run by scanning the extent and checksum trees. It allocates per-device buffers, locks the chunk range, reads stripe data in roughly 1 MiB batches, calls the RAID5 or RAID6 stripe checker for each stripe number, and writes back any stripe marked `rewrite`.
- `scrub_raid5_stripe()` identifies the rotating parity stripe, validates allocated data sectors by checksum or tree block header, verifies parity by XOR when all devices are present, repairs parity-only errors, and reconstructs one bad data sector/tree block from parity when possible.
- `scrub_raid6_stripe()` identifies rotating P and Q parity, validates data and both parity blocks, handles parity-only corrections, reconstructs a single missing/bad data block using available parity, and can reconstruct two data errors with Galois-field math when no device is missing. It logs unrecoverable cases when redundancy is insufficient or reconstructed data does not pass checksum/address validation.

## Chunk and Thread Orchestration

- `scrub_chunk()` takes the tree lock shared, chooses a scrub profile from the chunk flags, walks the extent tree from the current offset, identifies metadata extents versus data extents, loads data checksums from `checksum_root`, coalesces adjacent metadata tree runs, and calls the appropriate scrub helper. It advances the caller's offset and reports whether progress occurred.
- `scrub_thread()` initializes scrub statistics, flushes pending writes with `do_write()` when needed, frees cached trees, snapshots writable chunks into a local list, and processes each chunk until completion, pause, stop, or error. It uses `Vcb->scrub.event` for pause/resume gating, records duration, clears `c->reloc`, updates chunk counts under `stats_lock`, closes the thread handle, and signals `Vcb->scrub.finished`.

## Public Control Entry Points

- `start_scrub()` requires `SE_MANAGE_VOLUME_PRIVILEGE`, rejects locked volumes, active balance, already-running scrub, and read-only volumes, then starts `scrub_thread()` with `PsCreateSystemThread`.
- `query_scrub()` requires the same privilege, returns status/timing/progress/error counters, and serializes the variable-length scrub error list into caller-provided `btrfs_query_scrub` storage.
- `pause_scrub()` clears the event and accumulates elapsed duration.
- `resume_scrub()` sets the event and updates `resume_time`.
- `stop_scrub()` sets `stopping`, clears paused state, and wakes the scrub thread.

## Notable Details

- Scrub is intentionally write-capable: recoverable mirrored/parity errors are repaired in place unless the target device is read-only.
- Metadata validation includes both checksum and logical address checks; data validation depends on checksum items and skips sectors without data csums.
- RAID5/6 code locks physical chunk ranges during read/verify/rewrite to avoid concurrent relocation or write interference.
- Error reporting tries to translate physical failures into user-meaningful file paths or tree locations, but `log_unrecoverable_error()` has a FIXME noting it should still log something even if reference expansion fails.
- The implementation contains several dense pointer-offset expressions in checksum comparisons and RAID10/RAID6 recovery paths that are high-value review targets because mistakes there can change which sector is judged corrupt or repaired.
