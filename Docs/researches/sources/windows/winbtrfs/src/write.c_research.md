# File Research: sources/windows/winbtrfs/src/write.c

## Purpose

`write.c` is WinBtrfs’ core write path. It handles logical block allocation, chunk/stripe placement, RAID write preparation, device IRP fan-out, extent tree mutation, inline/preallocated extent conversion, cached and non-cached file writes, file growth/truncation, rollback bookkeeping, and the top-level `IRP_MJ_WRITE` dispatch.

## Main Responsibilities

- Allocate new Btrfs chunks for data, metadata, system, single, DUP, RAID0, RAID1, RAID10, RAID5, RAID6, RAID1C3, and RAID1C4 profiles.
- Select physical device holes and logical chunk addresses.
- Convert a logical write into one or more physical stripe writes.
- Generate RAID5/RAID6 parity and manage partial RAID56 stripes.
- Maintain file extents and checksums during copy-on-write, nocow, preallocation, truncation, and extension.
- Coordinate Windows cache manager interactions for cached writes and MDL writes.
- Dispatch write IRPs safely with locks, oplock checks, permissions, readonly checks, rollback, and notifications.

## Chunk Allocation

Key functions:

- `find_data_address_in_chunk()` finds a free logical range inside a chunk, loading the chunk cache if needed and choosing from `space_size`.
- `get_chunk_from_address()` maps a logical address to its owning chunk under `Vcb->chunk_lock`.
- `find_new_chunk_address()` chooses a new logical chunk offset after existing chunks, starting at `0xc00000`.
- `find_new_dup_stripes()` chooses two duplicate physical stripes, preferring least-used devices and allowing two regions on one device for DUP.
- `find_new_stripe()` chooses one stripe for non-DUP profiles, avoiding devices already selected for the same chunk unless degraded/missing handling allows it.
- `alloc_chunk()` computes chunk sizing, stripe count, missing-device tolerance, creates `CHUNK_ITEM`, updates device `bytes_used`, subtracts physical free-space regions, initializes chunk locks/lists, protects superblock regions, and inserts the new chunk into `Vcb->chunks`.

Important allocation behavior:

- Data chunks default to 1 GiB stripes and up to 10 GiB chunks.
- Metadata chunks use 256 MiB or 1 GiB stripes depending on total device size.
- System chunks use 32 MiB stripes.
- Chunk size is capped around 10 percent of total device capacity.
- RAID56 allocation sets `BTRFS_INCOMPAT_FLAGS_RAID56`.
- Degraded mode can add missing-device stripes for profiles that tolerate missing devices.

## Stripe Write Preparation

The file defines `write_stripe` as the per-stripe write range/MDL descriptor. Logical writes are expanded differently depending on chunk profile:

- `prepare_raid0_write()` maps logical data across striped devices using `get_raid0_offset()`, builds per-stripe MDLs, and handles page-aligned, unaligned, and file-write MDL sources.
- `prepare_raid10_write()` maps data across RAID0 stripe groups, then mirrors each group across `sub_stripes`.
- `prepare_raid5_write()` splits full-stripe writes, stores incomplete stripe data in `partial_stripe`, allocates parity buffers/MDLs, computes XOR parity with `do_xor()`, and prepares physical data/parity MDLs.
- `prepare_raid6_write()` is analogous to RAID5 but computes both P and Q parity, using `do_xor()` and `galois_double()`.
- `add_partial_stripe()` caches incomplete RAID56 writes until a full stripe is accumulated, then calls `flush_partial_stripe()`.

The RAID56 write path locks full stripe ranges through `get_raid56_lock_range()` and `chunk_lock_range()` to avoid overlapping parity updates.

## Device Write Dispatch

Key functions:

- `write_data()` creates `write_data_stripe` entries, builds physical write IRPs or associated IRPs, attaches MDLs/system buffers/user buffers according to lower-device I/O mode, validates missing-device tolerance, and queues stripe metadata in `write_data_context`.
- `write_data_complete()` wraps `write_data()`, launches stripe IRPs with `IoCallDriver()`, waits for completion, checks per-stripe status, logs device write errors, frees MDLs/IRPs/buffers, and unlocks RAID56 ranges.
- `write_data_completion()` stores child IRP status, cancels outstanding writes after an error, decrements `stripes_left`, and signals the context event.
- `free_write_data_stripes()` releases parity buffers, scratch buffers, master MDLs, per-stripe MDLs, child IRPs, and stripe records.

Important invariants:

- For mirrored profiles, identical logical data is written to every available stripe.
- Missing devices are tolerated only up to profile-specific limits.
- MDLs shared by RAID10 mirrored stripes are freed only once.
- RAID56 parity buffers are nonpaged and backed by MDLs.

## Extent Mutation

Key functions:

- `add_extent()` inserts an extent in offset order.
- `excise_extents()` removes or splits extents over a byte range. It handles inline extents, full removal, removal from beginning/end, and middle splits. It updates inode block counts, checksum slices, and extent reference deltas.
- `add_extent_to_fcb()` allocates and inserts a new in-memory extent, then records rollback.
- `remove_fcb_extent()` marks an extent ignored and records rollback rather than immediately deleting it.
- `insert_extent_chunk()` allocates space inside a chunk, creates `EXTENT_DATA`, optionally computes checksums, updates `c->used`, subtracts chunk free space, records changed extent refs, releases the chunk lock, and writes data if provided.
- `try_extend_data()` tries to append a new write into adjacent free space after the previous extent.
- `insert_chunk_fragmented()` falls back to filling available fragments across chunks.
- `insert_prealloc_extent()` creates preallocated extents, allocating new chunks as needed.
- `insert_extent()` is the main COW extent insertion loop and prefers extending existing chunks before allocating new chunks.

## File Size and Extent Operations

- `truncate_file()` removes data beyond the requested EOF, with special handling for inline files and conversion from inline to regular extents when needed.
- `extend_file()` handles alternate data streams, inline-file growth, conversion from inline extents to regular extents, preallocation, allocation-size updates, file-size updates, and valid-data-length updates.
- `do_write_file_prealloc()` converts written portions of preallocated extents into regular extents. It handles replacing all, beginning, end, or middle of the preallocated extent and updates checksums and extent refs.
- `do_write_file()` is the core noncached data modification routine. It chooses nocow/prealloc direct writes when possible, otherwise excises and inserts COW extents. It also validates extent ordering in `DEBUG_PARANOID`.

## Windows Write Path

- `write_file2()` performs the main high-level write operation:
  - validates file type and zero-length writes;
  - resolves append writes;
  - checks cache-manager write permission via `CcCanIWrite()`;
  - coordinates paging I/O locks, file locks, and tree locks;
  - extends files when writes pass EOF;
  - handles cached writes through `CcCopyWriteEx()`, `CcCopyWrite()`, and `CcPrepareMdlWrite()`;
  - handles alternate data stream writes in memory;
  - chooses inline, compressed, or normal extent write paths;
  - preserves partial-sector data through read-modify-write buffers;
  - updates inode times, sequence, transid, file sizes, root timestamps, dirty flags, and directory notifications.
- `write_file()` maps the user/system buffer, checks byte-range locks, invokes `write_file2()`, updates disk counters, and commits or rolls back mutations.
- `drv_write()` is the `IRP_MJ_WRITE` dispatch entry:
  - handles volume-device writes separately;
  - validates VCB, FCB, CCB, access rights, volume lock state, subvolume readonly state, and filesystem readonly state;
  - handles MDL write completion via `CcMdlWriteComplete()`;
  - checks oplocks for non-paging writes;
  - forces paging writes to wait;
  - completes the IRP or queues deferred work.

## Notable Dependencies

This file depends heavily on declarations and helpers from `btrfs_drv.h`, including:

- Btrfs structures: `device_extension`, `chunk`, `device`, `fcb`, `extent`, `EXTENT_DATA`, `EXTENT_DATA2`.
- Space/chunk helpers: `load_cache_chunk()`, `space_list_subtract()`, `space_list_subtract2()`, `protect_superblocks()`, `acquire_chunk_lock()`, `release_chunk_lock()`, `chunk_lock_range()`, `chunk_unlock_range()`.
- Extent/ref helpers: `add_changed_extent_ref()`, `update_changed_extent_ref()`, rollback helpers.
- Read/compression/checksum helpers: `read_file()`, `write_compressed()`, `do_calc_job()`.
- RAID helpers: `get_raid0_offset()`, `do_xor()`, `galois_double()`, `flush_partial_stripe()`.
- Windows kernel APIs: resources, IRPs, MDLs, cache manager, FsRtl locking/oplocks, and notification functions.

## Research Notes

This file is central to correctness. The highest-risk areas are RAID56 partial-stripe/parity handling, rollback correctness after partially completed extent mutations, MDL lifetime management, and interactions between cached writes, paging I/O, and tree/file locks. The code is careful about rollback and resource cleanup, but several comments mark known concurrency concerns, including a FIXME in `write_data_completion()` noting that cancellation/status updates need a lock.
