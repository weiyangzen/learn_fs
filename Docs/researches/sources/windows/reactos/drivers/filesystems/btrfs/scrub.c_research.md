# File Research: sources/windows/reactos/drivers/filesystems/btrfs/scrub.c

## Scope And Purpose

`scrub.c` implements the WinBtrfs/ReactOS Btrfs scrub engine. It walks allocated extents in every writable chunk, reads the physical stripes, verifies data checksums or metadata tree checksums, logs corruption with filesystem context, and repairs recoverable errors by rewriting bad mirrors or parity stripes. It also exposes the public scrub control/query operations: `start_scrub`, `query_scrub`, `pause_scrub`, `resume_scrub`, and `stop_scrub`.

Complete file read: 3452 lines.

## Main Structures

- `SCRUB_UNIT` is 1 MiB and bounds normal non-RAID56 scrub reads.
- `scrub_context` and `scrub_context_stripe` track asynchronous stripe reads for duplicate, RAID0, RAID1-like, RAID10, and single layout handling.
- `scrub_context_raid56` and `scrub_context_raid56_stripe` track full-stripe RAID5/6 reads, allocation bitmaps, checksum-presence bitmaps, tree/data classification, per-stripe error bitmaps, parity scratch buffers, and rewrite state.
- `path_part` is a temporary path reconstruction node used to translate checksum errors back into a user-visible subvolume/path/offset report.

## Error Attribution

The file invests substantial logic in making scrub errors actionable rather than only reporting a logical address.

- `log_file_checksum_error` reconstructs a file path from subvolume, inode, and offset. It follows `INODE_REF`, `INODE_EXTREF`, and `ROOT_BACKREF` records, handles subvolume boundaries, converts UTF-8 path bytes to UTF-16, and appends a `scrub_error` to `Vcb->scrub.errors`.
- `log_file_checksum_error_shared` handles shared data refs by reading the referencing leaf and finding matching `EXTENT_DATA` records.
- `log_tree_checksum_error` records metadata root, level, and first key when available.
- `log_tree_checksum_error_shared` follows shared block refs by reading the parent tree and finding the child pointer.
- `log_unrecoverable_error` looks up the extent item/metadata item for a corrupted address, parses inline and separate backrefs, and delegates to file/tree attribution helpers.
- `log_error` is the common entry point. Recoverable errors are directly recorded; unrecoverable errors are expanded through extent backrefs.

All scrub error list mutations and counters are protected by `Vcb->scrub.stats_lock`.

## Normal Stripe Scrubbing

`scrub_extent` prepares asynchronous IRPs for each stripe involved in a logical extent. It handles buffered, direct, and neither-buffered-nor-direct device I/O, waits for all reads through a completion event, updates `Vcb->scrub.data_scrubbed`, records read errors against devices, and then dispatches by layout:

- `scrub_extent_dup` handles duplicate, RAID1-like, RAID1C3/C4, and single layouts. With data checksums it validates against checksum items; for metadata it validates tree checksums and logical addresses. If one good copy exists, it logs recoverable errors and overwrites bad copies. If all copies are bad, it attempts sector/node-level reconstruction from any individually good copy.
- `scrub_extent_raid0` verifies each sector/node on its owning stripe. It can detect and log corruption but cannot recover because RAID0 has no redundancy.
- `scrub_extent_raid10` validates mirrored sub-stripes in RAID0 placement groups. It repairs bad mirrors from good mirrors when possible, falls back to sector/node-level validation when every mirror in a group initially looks bad, and writes repaired buffers back to writable devices.
- `scrub_data_extent` walks a bitmap where clear bits represent sectors with checksum coverage, splits runs into `SCRUB_UNIT` pieces, and calls `scrub_extent`.

## RAID5/RAID6 Scrubbing

RAID5/6 handling is separate because scrub must operate on full stripes with parity.

- `scrub_chunk_raid56` batches extents into contiguous stripe runs, limiting work by extent count and data volume.
- `scrub_chunk_raid56_stripe_run` builds allocation, checksum, and metadata bitmaps for the run by scanning the extent tree and checksum tree. It then reads physical stripes in bounded chunks, verifies device reads, calls RAID5 or RAID6 per-stripe logic, and writes any stripe buffers marked `rewrite`.
- `scrub_raid5_stripe` validates data/metadata sectors, recomputes XOR parity, detects parity-only errors, reconstructs a single bad data/metadata sector from parity, and logs unrecoverable cases when missing/corrupt state exceeds RAID5 tolerance.
- `scrub_raid6_stripe` validates P and Q parity, handles one- and two-error recovery using Galois-field operations, updates parity when needed, and distinguishes missing-device tolerance from actual checksum corruption.

The RAID56 code depends on helpers such as `do_xor`, `galois_double`, `galois_divpower`, `gmul`, `gdiv`, and `gpow2`, and it locks the affected chunk range while validating and rewriting.

## Chunk-Level Flow

`scrub_chunk` is the main extent walker for non-RAID56 layouts. It chooses the effective scrub layout from the chunk flags, acquires `Vcb->tree_lock` shared, walks `TYPE_EXTENT_ITEM` and `TYPE_METADATA_ITEM` records in the extent tree, loads data checksum coverage from `Vcb->checksum_root`, coalesces adjacent metadata nodes into `tree_run`s, and advances the caller’s offset after each processed extent. It intentionally caps each invocation to at most 64 extents or 128 MiB so the scrub thread can pause/stop between batches.

`scrub_thread` initializes scrub state, flushes pending writes through `do_write` when needed, snapshots writable chunks into a local work list, then iterates chunks until done or stopped. It waits on `Vcb->scrub.event` so pause/resume/stop can control forward progress, sets `c->reloc` while a chunk is being scrubbed, updates chunk counters and finish time under `stats_lock`, accumulates duration, closes the thread handle, and signals `Vcb->scrub.finished`.

## Public API Behavior

- `start_scrub` requires `SE_MANAGE_VOLUME_PRIVILEGE`, rejects locked volumes, concurrent balance, already-running scrub, and readonly mounts, initializes scrub state, and starts `scrub_thread`.
- `query_scrub` requires the same privilege, reports status/timing/progress/error fields, and serializes the variable-length scrub error list into `btrfs_query_scrub`.
- `pause_scrub` clears the scrub event and accounts elapsed duration.
- `resume_scrub` sets the event and refreshes `resume_time`.
- `stop_scrub` clears pause state, sets `stopping`, and wakes the worker.

## Integration Points

This file integrates with the driver’s extent tree, checksum tree, root/subvolume list, chunk/device model, async Windows IRP APIs, device statistics, writeback path, notification of scrub control state, and user-facing ioctl structures declared elsewhere in the driver.

Important external functions/macros include `find_item`, `find_next_item`, `read_data`, `write_data_phys`, `sync/read checksum helpers`, `check_tree_checksum`, `get_tree_checksum`, `check_sector_csum`, `get_sector_csum`, `do_calc_job`, `log_device_error`, `chunk_lock_range`, `chunk_unlock_range`, `do_write`, `free_trees`, and Btrfs layout constants.

## Risks And Notes

- The file is memory- and IRP-heavy; most paths free allocated buffers, MDLs, and IRPs, but correctness depends on every `goto end` path preserving initialized state.
- Several expressions look suspicious and should be reviewed separately: comparisons against `(uint8_t*)csum + (j + Vcb->csum_size)` where `j * Vcb->csum_size` seems intended, a check of `tp.item->key.obj_id == TYPE_EXTENT_ITEM` where `obj_type` likely matters, and `c->devices[j + j]->devobj` inside a loop over `k`.
- RAID5/6 recovery is complex and sensitive to off-by-one errors in stripe/parity mapping, especially with metadata nodes spanning multiple sectors.
- `query_scrub` serializes variable-length errors and returns `STATUS_BUFFER_OVERFLOW` when the caller buffer is too small, with `Information` set to required/used size semantics inherited from this implementation.
