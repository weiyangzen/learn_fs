# File Research: sources/windows/winbtrfs/src/balance.c

## Purpose

`balance.c` implements WinBtrfs balance, chunk relocation, profile conversion, balance resume/pause/stop/query IOCTL support, and device removal/shrink workflows. It moves data and metadata extents out of selected chunks, rewrites extent/backreference metadata, commits the transaction, and coordinates long-running balance state through a kernel thread.

## Core Data Structures

- `metadata_reloc`
  - Tracks a relocated metadata tree block: old address, new address, loaded `tree_header`, original `EXTENT_ITEM`, whether it belongs to system space, associated in-memory `tree`, and metadata refs.
- `metadata_reloc_ref`
  - Represents `TREE_BLOCK_REF` or `SHARED_BLOCK_REF` references for a metadata block.
  - Stores parent relocation state so shared refs can be rewritten from old parent addresses to new parent addresses.
- `data_reloc`
  - Tracks a relocated data extent: old logical address, size, new address, new chunk, original `EXTENT_ITEM`, and data refs.
- `data_reloc_ref`
  - Represents `EXTENT_DATA_REF` or `SHARED_DATA_REF` references for a data extent, with parent metadata relocation for shared refs.
- `BALANCE_UNIT`
  - Limits data relocation reads/writes to 1 MiB at a time.

## Metadata Relocation

- `add_metadata_reloc()`
  - Removes an existing metadata extent item from the extent tree.
  - Decrements old chunk usage and adds the old tree block range back to free space.
  - Parses inline `TREE_BLOCK_REF` and `SHARED_BLOCK_REF` records.
  - Scans following non-inline ref items if the inline refcount is smaller than the extent item refcount.
  - Adds a `metadata_reloc` object to the pending relocation list.
- `add_metadata_reloc_parent()`
  - Reuses an already queued `metadata_reloc` for a parent address when present.
  - Otherwise finds the parent block’s `METADATA_ITEM` or tree `EXTENT_ITEM` and queues it for relocation too.
- `sort_metadata_reloc_refs()`
  - Sorts refs into on-disk order before rebuilding extent items.
- `add_metadata_reloc_extent_item()`
  - Recreates the relocated metadata extent item at the new address.
  - Uses skinny metadata when enabled; otherwise writes `EXTENT_ITEM2` with first item and level.
  - Splits refs between inline refs and separate ref items when inline data would exceed one quarter of node size.
  - Rewrites shared metadata/data backrefs inside child tree blocks or leaf extent-data items when the parent block address changes.

## Metadata Write Path

`write_metadata_items()` is the central metadata relocation writer:

- Reads each old tree block into memory.
- Detects whether the original block came from system space.
- If data relocation is also in progress, updates leaf `EXTENT_DATA` physical addresses from old data extents to new data extents.
- Finds parent tree blocks or root items that refer to each moved block.
- Allocates new metadata addresses by level, preferring a recently allocated chunk, then compatible existing chunks, then a new chunk.
- Updates parent internal-node pointers, loaded tree-data holders, root treeholder addresses, and superblock root/chunk tree addresses.
- Updates in-memory tree hash lists when a loaded tree’s address changes.
- Recomputes tree checksums and queues physical tree writes.
- Calls `do_tree_writes()` and then recreates relocated metadata extent items.
- Cleans up queued `tree_write` records on exit.

`balance_metadata_chunk()` scans the extent tree for metadata extents in a selected chunk, queues up to 64 metadata blocks per pass, calls `write_metadata_items()`, commits via `do_write()`, applies rollback on failure, frees cached trees, and reports whether anything changed.

## Data Relocation

- `data_reloc_add_tree_edr()`
  - Resolves an `EXTENT_DATA_REF` to the owning root/inode.
  - Scans the file’s `EXTENT_DATA` items to find references to the relocating extent.
  - Groups adjacent references from the same leaf tree.
  - Adds the containing leaf tree to metadata relocation so the file extent item can be rewritten.
- `add_data_reloc()`
  - Deletes the old data extent item.
  - Decrements old chunk usage and frees the old logical range.
  - Parses inline and non-inline `EXTENT_DATA_REF` / `SHARED_DATA_REF` records.
  - For shared data refs, queues the parent metadata block for relocation.
- `sort_data_reloc_refs()`
  - Sorts refs by type/hash and coalesces duplicate `EXTENT_DATA_REF` records by summing counts.
- `add_data_reloc_extent_item()`
  - Recreates the relocated data extent item at the new address.
  - Emits inline refs up to the node-size limit and separate ref items beyond that.

`balance_data_chunk()` relocates actual file data:

- Scans data `EXTENT_ITEM`s in a selected chunk, excluding tree-block extents.
- Processes at most 16 MiB or 100 extents per pass.
- Allocates destination data ranges from compatible non-reloc chunks or a newly allocated data chunk.
- Builds a bitmap of sectors with checksums by reading checksum-tree items.
- Copies no-checksum and checksum-covered runs in `BALANCE_UNIT` chunks.
- For checksum-covered runs, verifies reads using old checksums, writes data to the new extent, inserts new checksum items, and removes old checksum items.
- Calls `write_metadata_items()` for the metadata leaves that point at moved extents.
- Recreates data extent items at the new logical addresses.
- Moves matching `changed_extent` records to the destination chunk.
- Updates free-space-cache inode extents before commit and open FCB extent mappings after successful commit.
- Commits through `do_write()`, clears or rolls back relocation state, frees cached trees, and releases relocation objects.

## Balance Filters And Persistent State

- `get_chunk_dup_type()` extracts the chunk’s profile: single, dup, RAID0/1/10/5/6/1C3/1C4.
- `should_balance_chunk()` applies per-class balance filters:
  - enabled flag
  - profiles
  - device id
  - device range
  - virtual range
  - stripe count
  - usage percentage
  - soft convert skip when already in target profile
- `copy_balance_args()` converts in-memory `btrfs_balance_opts` to on-disk `BALANCE_ARGS`.
- `add_balance_item()` writes a root-tree `BALANCE_ITEM` so an interrupted balance can be resumed.
- `remove_balance_item()` deletes the persistent balance item after a normal balance completes.
- `load_balance_args()` reconstructs in-memory balance options from a persisted `BALANCE_ITEM`.
- `look_for_balance_item()` is the mount-time/resume path:
  - finds `BALANCE_ITEM`;
  - loads data/metadata/system options;
  - applies Linux-like heuristics: convert balances become soft, and non-convert balances without usage filters get a 0-90% usage filter;
  - pauses if readonly or `skip_balance` is set;
  - starts `balance_thread()`.

## Device Removal And Shrink

- `remove_device()` validates privilege, target device existence, readonly state, active balance state, and RAID minimum-device constraints.
  - It refuses to remove the last writable device.
  - It rejects removals that would violate RAID0/1/5/6/10/1C3/1C4 requirements.
  - It starts a balance in removal mode with all chunk classes filtered by `devid`.
- `finish_removing_device()`
  - Flushes outstanding writes.
  - Removes the device’s `DEV_ITEM` and `DEV_STATS`.
  - Decrements superblock device counters and total size.
  - Commits the removal.
  - Zeroes superblocks on the removed device when writable.
  - Updates the volume child list and mount manager state.
  - Re-adds drive letters for a removed child that previously had one.
  - Updates removable-media characteristics, trim state, and notifies volume-size change.
- `trim_unalloc_space()`
  - Builds TRIM ranges for all unallocated device regions, avoiding superblock locations and the first MiB.
  - Issues `IOCTL_STORAGE_MANAGE_DATA_SET_ATTRIBUTES` with `DeviceDsmAction_Trim`.
- `regenerate_space_list()`
  - Rebuilds a device’s free-space list after shrink failure/cancel by starting with all space after the first MiB and subtracting every stripe allocation.
- Shrink completion in `balance_thread()` updates `devitem.num_bytes`, rewrites the device item, adjusts `superblock.total_bytes`, commits, or regenerates the space list on failure.

## Balance Thread Control Flow

`balance_thread()` is the long-running kernel worker:

1. Increments `balance_num` and initializes thread state.
2. Applies requested profile conversions by changing `Vcb->data_flags`, `metadata_flags`, and `system_flags`.
3. Mirrors data/metadata options for mixed block groups.
4. Writes `BALANCE_ITEM` for normal balances, or flushes pending writes for removal/shrink.
5. Waits on `Vcb->balance.event`, supporting pause/resume.
6. Scans chunks and builds a selected chunk list using `should_balance_chunk()`.
7. Loads chunk free-space caches before relocation.
8. For full balances with no already-acceptable chunks, preallocates a destination chunk or calls `try_consolidation()`.
9. Marks selected chunks as `reloc`.
10. Relocates data chunks first, then metadata/system chunks.
11. On stop/error, clears relocation flags and restores old profile flags.
12. Finishes device removal or shrink when requested.
13. Removes the persistent balance item for normal balances.
14. Trims unallocated space after successful operations when enabled.
15. Closes the thread handle, clears `Vcb->balance.thread`, and signals `balance.finished`.

`try_consolidation()` supports out-of-space full balances by relocating least-used data chunks not yet handled in the current balance, then allocating a destination chunk.

## Public Entry Points

- `start_balance()`
  - IOCTL entry point for starting a balance.
  - Requires `SE_MANAGE_VOLUME_PRIVILEGE`.
  - Rejects locked volumes, active scrub, active balance, readonly volumes, and empty option sets.
  - Validates profile, devid, range, limit, stripe, usage, and convert options.
  - Copies options into `Vcb->balance`, initializes events/status, and starts `balance_thread()`.
- `query_balance()`
  - Reports stopped/running/paused status, removal/shrink flags, error status, chunks left/total, and active options.
- `pause_balance()`
  - Requires privilege, active running balance, and clears the balance event.
- `resume_balance()`
  - Requires privilege, active paused balance, writable volume, and sets the balance event.
- `stop_balance()`
  - Requires privilege, marks the balance as stopping, clears paused state, sets success status, and wakes the thread.

## Important Dependencies

This file depends heavily on WinBtrfs transaction and tree helpers:

- tree search/mutation: `find_item`, `find_next_item`, `find_item_to_level`, `insert_tree_item`, `delete_tree_item`
- extent accounting: `increase_extent_refcount`, `decrease_extent_refcount`, `find_extent_shared_tree_refcount`, `find_extent_shared_data_refcount`
- allocation/free space: `alloc_chunk`, `find_metadata_address_in_chunk`, `find_data_address_in_chunk`, `space_list_add`, `space_list_subtract`, `load_cache_chunk`
- I/O: `read_data`, `write_data_complete`, `write_data_phys`, `do_tree_writes`
- transaction control: `do_write`, `clear_rollback`, `do_rollback`, `free_trees`
- checksum tree updates: `add_checksum_entry`
- Windows kernel primitives: `ERESOURCE`, `KEVENT`, `PsCreateSystemThread`, `ZwClose`, `FsRtlNotifyVolumeEvent`, storage TRIM IOCTLs, mount manager IOCTLs

## Notable Edge Cases

- `start_balance()` appears to normalize `USAGE` using `stripes_start` / `stripes_end` instead of `usage_start` / `usage_end`, and checks the stripe fields for the usage range. That looks like a validation bug.
- `should_balance_chunk()` checks `num_stripes < stripes_start || num_stripes < stripes_end`; the second comparison likely should reject values above `stripes_end`.
- Several relocation helpers mutate extent-tree and chunk free-space state before later allocations or tree rewrites can fail. Rollback lists are used, but correctness depends on every changed path being represented in rollback state.
- Some allocation-failure paths after deleting tree items or extent refs return directly and rely on the outer rollback/commit structure; leaks of partially allocated relocation refs are possible until the end cleanup walks the lists.
- `balance_thread()` owns long-running state through shared `Vcb->balance` fields without a single dedicated balance lock; correctness depends on event/state discipline and existing tree/chunk locks.
- Device removal updates mount-manager and child-device structures after on-disk commit, so failures in those later notification paths are logged but do not roll back the filesystem removal.
