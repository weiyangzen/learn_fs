# File Research: sources/windows/reactos/drivers/filesystems/btrfs/write.c

## Role

This is the central WinBtrfs write path. It handles Btrfs chunk allocation, data-stripe preparation for single/mirrored/striped/parity profiles, physical child-device write IRPs, extent-list mutation, copy-on-write and no-COW/prealloc writes, file growth/truncation, cached and noncached write dispatch, alternate data stream writes, timestamps/notifications, rollback, and IRP completion for `IRP_MJ_WRITE`.

The file bridges Windows write semantics and Btrfs on-disk allocation semantics. It turns file writes into Btrfs extents and checksums, updates chunk free-space and reference tracking, sends data to the correct device stripes, and keeps the in-memory FCB/VCB state dirty for later metadata commit.

## Major Responsibilities

- Find free logical addresses inside existing chunks.
- Allocate new chunks for DATA, METADATA, SYSTEM, DUP, RAID0, RAID1, RAID10, RAID5, RAID6, RAID1C3, and RAID1C4 profiles.
- Select stripe devices based on free-space holes and approximate device usage.
- Prepare write MDLs for RAID0 and RAID10 striped writes.
- Buffer partial RAID5/6 stripes and flush them once complete.
- Generate RAID5 XOR parity and RAID6 P/Q parity.
- Send parallel write IRPs to child devices and wait for completion.
- Track missing-device tolerances by profile.
- Split, remove, insert, and roll back file extents.
- Allocate checksums unless `BTRFS_INODE_NODATASUM` is set.
- Convert inline extents to regular extents and regular extents back to inline where applicable.
- Extend/truncate file sizes and preallocate physical space.
- Handle cached writes through Cache Manager and noncached writes through direct Btrfs extent writes.
- Update inode times, sequence, subvolume root timestamps, file sizes, cache file sizes, disk counters, and directory notifications.
- Dispatch and complete write IRPs, including volume-FDO raw writes and MDL write completion.

## Chunk Free-Space Lookup

`find_data_address_in_chunk()` verifies the requested length fits remaining chunk capacity, loads the chunk cache if needed, and searches `c->space_size` for a hole:

- Exact hole size is preferred.
- If the list reaches a hole smaller than requested, it chooses the previous larger hole.
- If all listed holes are larger and the tail hole is large enough, it chooses the tail.

`get_chunk_from_address()` scans `Vcb->chunks` under `chunk_lock` and returns the chunk whose logical address range contains the requested address.

`find_new_chunk_address()` picks a logical chunk offset by scanning existing chunks from `0xc00000` and returning the first gap large enough for the new chunk.

## Chunk Allocation

`alloc_chunk()` chooses chunk and stripe sizes, selects devices/holes, builds a `CHUNK_ITEM`, creates the in-memory `chunk`, initializes locks/lists/events, subtracts device space, protects superblock-reserved areas, inserts the chunk in logical order, marks it created/changed, and returns it.

Profile policy:

- DATA chunks use up to 1 GiB per stripe and up to 10 GiB per chunk.
- METADATA chunks use 1 GiB per stripe above 50 GiB total device size, otherwise 256 MiB.
- SYSTEM chunks use 32 MiB stripes and 64 MiB max chunk size.
- Max chunk size and stripe size are capped to roughly 10 percent of total device size.
- RAID5/6 set the RAID56 incompat flag.

Stripe selection:

- `find_new_stripe()` chooses a hole on a writable, non-relocating, present device, avoiding devices already selected for the same chunk. It favors the least-used device and a hole that fits `max_stripe_size`; if allowed and not full-size, it falls back to the largest available hole.
- `find_new_dup_stripes()` finds two holes on one device for DUP, again favoring least-used devices, and can split a single large hole into two DUP stripes.
- Degraded allocation can add missing-device stripes when `Vcb->options.allow_degraded` permits it and the profile has allowed missing stripes.

The function initializes `c->space` and `c->space_size` with one free logical range, creates `range_locks`, `partial_stripes`, `changed_extents`, and chunk resources, and updates each selected device's `bytes_used`.

## Stripe Write Preparation

`write_data()` is the profile dispatcher. It finds the target chunk, allocates a `write_stripe` array, calls the appropriate preparation routine, checks whether missing devices exceed profile tolerance, creates per-stripe `write_data_stripe` records and IRPs, and records total physical bytes for disk counters.

Profile behavior:

- Single/DUP/RAID1/RAID1C3/RAID1C4 write the same logical data to every present stripe and allow all but one stripe to be missing.
- RAID0 uses `prepare_raid0_write()` and allows no missing devices.
- RAID10 uses `prepare_raid10_write()` and allows one missing device.
- RAID5 uses `prepare_raid5_write()` and allows one missing device.
- RAID6 uses `prepare_raid6_write()` and allows two missing devices.

`prepare_raid0_write()` and `prepare_raid10_write()` compute per-stripe logical ranges, build partial MDLs over the caller or scratch buffer, and split page frame numbers by stripe. RAID10 mirrors each logical stripe across `sub_stripes`.

For non-file writes or unaligned buffers, these routines may allocate a nonpaged scratch copy or probe/lock an MDL over the kernel buffer.

## RAID5/6 Partial Stripes And Parity

`add_partial_stripe()` stores partial RAID5/6 full-stripe writes in `c->partial_stripes`. It uses a bitmap where set bits mean missing sectors. When the bitmap becomes fully clear, it calls `flush_partial_stripe()`, removes the partial-stripe record, and frees its bitmap/data.

`prepare_raid5_write()`:

- Moves unaligned head/tail fragments into partial-stripe storage.
- Computes per-data-stripe ranges and parity range.
- Allocates log-stripe MDLs for data used to calculate parity.
- Allocates `wtc->parity1` and its MDL.
- Builds stripe MDLs, copies PFNs into data and parity stripes, maps log MDLs, and XORs all data stripes into `parity1`.

`prepare_raid6_write()` follows the same shape but reserves two parity stripes, allocates `parity1` and `parity2`, and computes RAID6 parity by XORing data for P and repeatedly applying `galois_double()` plus XOR for Q.

`get_raid56_lock_range()` maps a logical write to the full RAID5/6 stripe range that must be serialized. `write_data_complete()` uses this to lock parity ranges around `write_data()` and child-IRP completion.

## Physical Child Writes

`write_data_complete()` initializes a `write_data_context`, optionally locks RAID5/6 stripe ranges, calls `write_data()` under SEH, launches all non-ignored child write IRPs with `IoCallDriver()`, waits on a context event, checks each stripe status, logs device write errors, frees all stripe/MDL/parity/scratch resources, unlocks RAID5/6 ranges, and returns status.

`write_data_completion()` copies child IRP status, marks the stripe success/error/cancelled, cancels sibling pending IRPs on error, decrements `stripes_left`, and signals when the final stripe completes. A source comment says a lock is needed here; list and status updates are currently unsynchronized.

`free_write_data_stripes()` releases parity MDLs, scratch MDLs, parity buffers, scratch buffer, stripe MDLs, IRPs, and stripe records. It tracks `last_mdl` to avoid freeing the same MDL multiple times for RAID10 mirrored stripes.

## Extent Mutation

`add_extent()` inserts an extent into an FCB's extent list sorted by logical file offset.

`remove_fcb_extent()` marks an extent ignored and records a rollback entry.

`add_extent_to_fcb()` allocates a new `extent`, copies `EXTENT_DATA`, attaches checksum ownership, inserts it sorted by offset, and records an insert rollback.

`excise_extents()` removes or splits existing extents overlapping a byte range. It handles:

- Whole inline extent removal.
- Whole regular/prealloc extent removal, including changed extent reference decrement.
- Removing the beginning of an extent.
- Removing the end of an extent.
- Removing the middle, creating two replacement extents and increasing changed extent references as needed.

Checksum slices are copied for uncompressed extents. Compressed extents keep checksum buffers covering the whole compressed physical extent. Inline extents cannot be split; attempting to split one returns an internal error. The function marks extents and inode items changed and dirties the FCB.

## New Extent Insertion

`insert_extent_chunk()` assumes the caller holds `c->lock`; on success it releases the chunk lock. It finds free space in the chunk, allocates `EXTENT_DATA`/`EXTENT_DATA2`, calculates checksums when data is present and checksums are enabled, inserts the extent into the FCB, subtracts logical free space, increments inode blocks, marks dirty state, records a changed extent reference, releases the chunk lock, and writes data to the physical address if data was supplied.

`try_extend_data()` tries to append a write to the physical free space immediately after the previous file extent, when the chunk is writable/non-relocating and has the same data profile. It still creates a new extent record for the appended range.

`insert_extent()` breaks a write into `MAX_EXTENT_SIZE` pieces, tries to reuse existing chunks, allocates new chunks if necessary, falls back to fragmented insertion when allocation cannot provide a large enough contiguous region, and uses `insert_extent_chunk()` for each physical allocation.

`insert_chunk_fragmented()` allocates as many chunks as it can, then walks every writable data chunk and consumes holes in size order until the requested logical range is covered or disk space runs out.

`insert_prealloc_extent()` creates prealloc extents for file allocation. It tries existing chunks, then new chunks, then fragmented allocation, and avoids prealloc marking for paging files.

## File Truncation And Extension

`truncate_file()`:

- If truncating an inline file to a nonzero size, reads the remaining data, removes old extents, then either writes it as regular sector-aligned data or creates a shorter inline extent.
- Otherwise excises extents beyond the aligned new EOF.
- Updates inode size, allocation size, file size, and valid data length.
- Notes a FIXME to notify Cache Manager for the non-inline path.

`extend_file()`:

- Handles alternate data streams by delegating to `stream_set_end_of_file_information()`.
- Finds the last non-ignored extent and current allocation.
- Converts inline files to regular extents when the new size exceeds `max_inline`.
- Extends inline data in place by replacing the inline extent with a larger zero-padded inline extent.
- Optionally inserts prealloc extents for regular files.
- Creates either regular allocation or inline zero-filled data when extending a previously empty file.
- Updates inode size, blocks, FCB file sizes, dirty flags, and allocation size.

## Preallocated And No-COW Writes

`do_write_file_prealloc()` converts a prealloc extent, or a slice of one, into regular written extents:

- Replaces whole prealloc extents with a regular extent and writes the full range in place.
- Replaces beginning, end, or middle portions by splitting into regular and remaining prealloc extents.
- Calculates checksums for newly written regular portions when required.
- Updates changed extent references for split cases.
- Marks the underlying chunk changed.

`do_write_file()` is the core noncached logical write function:

- Walks file extents overlapping the write range.
- For unique no-COW regular extents, writes in place directly to the existing physical address.
- For unique prealloc extents, calls `do_write_file_prealloc()`.
- For gaps or copy-on-write ranges, excises existing extents and calls `insert_extent()`.
- Updates checksums in place for unexpected NODATACOW-with-checksums cases.
- Validates extent ordering in `DEBUG_PARANOID`.
- Marks extents changed and dirties the FCB.

## Top-Level Write Flow

`write_file2()` implements Windows file write semantics around the Btrfs write engine:

- Rejects zero-length writes as success.
- Validates the `FILE_OBJECT`, FCB type, and append-to-EOF sentinel.
- Uses `CcCanIWrite()` for cached throttling and rejects async noncached writes by returning `STATUS_PENDING`.
- For noncached nonpaging writes with cached sections, flushes and purges Cache Manager data under the paging resource.
- Acquires paging, tree, and FCB resources according to paging/pagefile mode.
- Extends file size when writes pass EOF, except paging writes past EOF are clipped or ignored.
- Initializes or resizes Cache Manager file sizes for cached writes.
- Handles MDL cached writes with `CcPrepareMdlWrite()`.
- Handles normal cached writes with `CcCopyWriteEx()` when available, otherwise `CcCopyWrite()`, always waiting to avoid flush-before-worker races.
- Handles alternate data stream growth and buffer writes in-memory.
- Handles noncached regular writes by choosing inline, compressed, or normal sector-aligned write ranges, reading partial old data when needed, then calling `add_extent_to_fcb()`, `write_compressed()`, or `do_write_file()`.
- Updates inode timestamps, sequence, size, dirty flags, subvolume root time, Cache Manager file sizes, current byte offset, and notifications.

`write_file()` maps the caller buffer from `SystemBuffer` or MDL/user buffer, checks byte-range locks, initializes rollback, calls `write_file2()`, updates disk counters for noncached writes, and either clears or applies rollback depending on status.

`drv_write()` is the `IRP_MJ_WRITE` dispatch routine:

- Enters filesystem context and top-level IRP handling.
- Routes volume-device writes to `vol_write()`.
- Validates VCB, FCB, CCB, user access, volume-lock state, readonly subvolume, and readonly volume state.
- Passes locked-volume raw writes to `Vpb->RealDevice`.
- Handles `IRP_MN_COMPLETE` by calling `CcMdlWriteComplete()`.
- Checks oplocks for nonpaging writes.
- Forces synchronous handling for paging I/O to avoid Cache Manager deadlocks.
- Calls `write_file()`.
- Completes nonpending IRPs; for `STATUS_PENDING`, marks pending and queues a worker job with `add_thread_job()`, falling back to immediate `do_write_job()` if queueing fails.

## Dependencies And Integration Points

This file depends on the rest of the WinBtrfs driver for chunk locking, changed extent references, free-space list operations, checksum calculation, compressed writes, file reads, rollback, notifications, stream metadata, cache initialization, volume raw writes, PnP volume state, and device error logging. It also depends on Windows kernel APIs for IRPs, MDLs, Cache Manager, FsRtl resources/oplocks/locks, disk counters, SEH, and paging-file priorities.

Key external helpers include `load_cache_chunk()`, `space_list_subtract()`, `space_list_subtract2()`, `protect_superblocks()`, `acquire_chunk_lock()`, `release_chunk_lock()`, `chunk_lock_range()`, `chunk_unlock_range()`, `flush_partial_stripe()`, `do_xor()`, `galois_double()`, `do_calc_job()`, `update_changed_extent_ref()`, `add_changed_extent_ref()`, `write_compressed()`, `read_file()`, `stream_set_end_of_file_information()`, `mark_fcb_dirty()`, `mark_fileref_dirty()`, and rollback helpers.

## Risk Notes

- `write_data_completion()` explicitly lacks locking while changing stripe states and cancelling sibling IRPs.
- The RAID preparation code performs low-level PFN copying and partial MDL construction; it assumes page-aligned lengths and offsets in several paths.
- `insert_extent_chunk()` releases `c->lock` internally only after a successful insertion, making its lock ownership contract unusual and easy to misuse.
- Many extent split paths allocate multiple replacement extents and checksum buffers before removing the original; rollback coverage is essential for correctness.
- `truncate_file()` notes that Cache Manager should be informed for one truncation path.
- `drv_write()` may queue pending writes to a worker; paging I/O is forced to wait to avoid deadlocks.
