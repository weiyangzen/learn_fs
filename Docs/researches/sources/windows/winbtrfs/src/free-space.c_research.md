# File Research: sources/windows/winbtrfs/src/free-space.c

## Purpose

`free-space.c` implements WinBtrfs per-chunk free-space tracking, legacy inode-backed free-space cache handling, Btrfs free-space-tree handling, and the rollback-aware in-memory list operations used by allocation, balance, and transaction commit paths. It can clear stale on-disk caches, load existing free-space state, reconstruct it from the extent tree, serialize it back to cache inodes or the free-space tree, and keep address-sorted and size-sorted free-space lists consistent as extents are allocated or freed.

## Core State

- `chunk::space`
  - Address-sorted list of free ranges available in a chunk.
- `chunk::space_size`
  - Size-sorted companion list for the same `space` nodes, ordered with larger entries first.
- `chunk::deleting`
  - Ranges becoming free in the current transaction; merged into serialized cache state when updating caches.
- `chunk::cache`
  - FCB for the legacy free-space cache inode associated with a chunk.
- `chunk::old_cache`
  - Holds an invalidated cache inode after deletion so later cleanup can finish safely.
- `chunk::cache_loaded`
  - Prevents repeated reconstruction/loading.
- `chunk::changed` and `chunk::space_changed`
  - Mark chunk metadata and free-space state as needing writeback.
- `CACHE_INCREMENTS`
  - Legacy cache inode allocation granularity in sectors, set to `64`.
- `superblock_stripe`
  - Temporary list node used to count chunk stripes occupied by Btrfs superblock mirrors so those protected regions are excluded from available free space.

## Cache Clearing

- `remove_free_space_inode()`
  - Opens a root-tree cache inode by object id, marks it dirty, excises all extents when it has data, marks it deleted, flushes the FCB, and releases it.
  - Uses the caller-provided rollback list for extent excision.
- `clear_free_space_cache()`
  - Deletes all root-tree `FREE_SPACE_CACHE_ID` items and removes the cache inodes they reference.
  - Drops any matching `chunk::cache` FCBs already attached to chunks.
  - If a free-space tree exists, deletes all items from `Vcb->space_root`.
  - If the filesystem uses the free-space-tree compat-ro feature, reloads each unloaded chunk cache, then marks the chunk as changed so the free-space tree can be regenerated.
  - Maintains rollback for inode extent removal but returns directly on many tree deletion failures.

## In-Memory Free-Space List Helpers

- `add_space_entry()`
  - Allocates a `space` record and inserts it into an address-sorted list.
  - Optionally inserts the same node into `list_size`, sorted by descending range size.
  - Does not merge adjacent entries; callers merge separately after bulk loads.
- `order_space_entry()`
  - Repositions one existing `space` node into the size-sorted list.
- `space_list_add2()`
  - Adds a free range to an arbitrary `space` list.
  - Handles full containment, new-range containment of existing entries, overlap at either edge, adjacency with the previous or next range, and insertion of a disjoint range.
  - Updates `list_size` when supplied and records rollback actions when supplied.
- `space_list_add()`
  - Marks the chunk changed and adds the range to `chunk::deleting`, not directly to `chunk::space`.
- `space_list_subtract2()`
  - Removes an allocated range from an arbitrary free-space list.
  - Handles full entry deletion, removing from the start or end, and splitting an entry into two ranges.
  - Updates the size-sorted companion list and records rollback actions when supplied.
- `space_list_subtract()`
  - Marks the chunk changed and subtracts from both committed free space and pending-deleting ranges.
- `space_list_merge()`
  - Adds every range from a source list into a destination list, used mainly to combine `space` and `deleting`.
- `copy_space_list()`
  - Duplicates address-sorted `space` records into a new list for cache serialization.
- `add_rollback_space()`
  - Wraps a range change in a `rollback_space` record and appends either `ROLLBACK_ADD_SPACE` or `ROLLBACK_SUBTRACT_SPACE`.

## Legacy Cache Loading

- `load_stored_free_space_cache()`
  - Finds the root-tree `FREE_SPACE_CACHE_ID` item for the chunk and opens the inode it points to.
  - In `load_only` mode, only attaches the FCB and returns.
  - Rejects zero-length cache files, chunks below 100 MiB, generation mismatches, malformed sizes, invalid checksums, unknown entry types, and total-space mismatches.
  - Reads the whole cache inode, verifies the embedded cache generation, verifies per-sector CRC32C checksums, parses `FREE_SPACE_ENTRY` records, and decodes bitmap records with `load_free_space_bitmap()`.
  - Calls `get_superblock_size()` and checks that parsed free space plus protected superblock space equals `chunk_size - used`.
  - Merges adjacent parsed entries and reorders their size-list nodes.
  - On invalid cache contents, deletes the root-tree cache item, excises cache inode extents, marks the cache FCB deleted, moves it to `old_cache`, clears parsed free-space entries, and returns `STATUS_NOT_FOUND`.
- `load_free_space_bitmap()`
  - Inverts the on-disk bitmap dwords, initializes an `RTL_BITMAP`, finds clear runs, and adds those runs as free ranges.
  - Accumulates total parsed free space for sanity checking.
- `get_superblock_size()`
  - Computes how much logical chunk space must be protected for Btrfs superblock mirror locations.
  - Handles RAID0/RAID10, RAID5, RAID6, and single/dup/RAID1/RAID1C3/RAID1C4 mapping separately.
  - Deduplicates affected logical stripes via `add_superblock_stripe()` and returns protected bytes as stripe count times `stripe_length`.

## Free-Space Tree Loading

- `load_stored_free_space_tree()`
  - Requires `Vcb->space_root` and a valid `TYPE_FREE_SPACE_INFO` item for the chunk.
  - Walks following free-space-tree items until leaving the chunk range.
  - Adds `TYPE_FREE_SPACE_EXTENT` items directly as free ranges.
  - Decodes `TYPE_FREE_SPACE_BITMAP` items by copying bitmap data to an aligned buffer, finding clear runs, and adding the corresponding free ranges.
  - Merges adjacent parsed ranges after the walk.
  - Does not validate the parsed total against `chunk_size - used`; the legacy cache loader has the stronger total-space sanity check.

## Cache Generation Fallback

- `load_free_space_cache()`
  - Chooses the source of free-space state:
    - If free-space-tree flags are present and valid, loads from `Vcb->space_root`.
    - Else if the superblock cache generation matches `generation - 1`, tries the legacy inode-backed cache.
    - Else treats stored cache data as missing.
  - If stored loading returns `STATUS_NOT_FOUND`, reconstructs the free-space list by scanning the extent tree from the chunk start.
  - Treats `TYPE_EXTENT_ITEM` ranges as used by their key offset and `TYPE_METADATA_ITEM` ranges as used by `node_size`.
  - Inserts gaps between used extents as free ranges and adds any trailing chunk space after the final used extent.
- `load_cache_chunk()`
  - Public loader wrapper for one chunk.
  - Skips already loaded chunks, calls `load_free_space_cache()`, protects superblock regions with `protect_superblocks(c)`, and marks the chunk cache loaded.

## Legacy Cache Allocation

- `insert_cache_extent()`
  - Allocates physical storage for a cache inode using the filesystem data profile.
  - Prefers existing writable, non-relocation chunks with enough room, then allocates a new data chunk.
  - Calls `insert_extent_chunk()` to attach the extent to the cache FCB.
- `allocate_cache_chunk()`
  - Ensures one chunk has a legacy cache inode and enough allocated cache-file space.
  - Counts current free-space entries plus pending-deleting entries, computes the cache inode size with checksum area, generation field, entry padding, and `CACHE_INCREMENTS` alignment.
  - Creates a new cache FCB and root-tree `FREE_SPACE_CACHE_ID` item when absent.
  - Reallocates extents when the cache needs to grow or when existing cache extents sit in readonly or relocation chunks.
  - When no reallocation is needed, makes sure the cache inode item and `FREE_SPACE_ITEM` are present and marked writable in the tree cache.
  - Leaves bitmap serialization unimplemented; all serialized entries are extents.
- `allocate_cache()`
  - Walks all chunks under `chunk_lock`.
  - For changed chunks of at least 100 MiB, calls `allocate_cache_chunk()`.
  - Commits all FCB/tree changes through a batch list and reports whether any cache allocation changed on-disk metadata.

## Legacy Cache Updating

- `update_chunk_cache()`
  - Serializes one chunk's legacy cache inode.
  - Copies `chunk::space`, copies `chunk::deleting`, merges them, writes each range as a `FREE_SPACE_EXTENT` entry, and updates the cache inode timestamps/generation/sequence.
  - Updates the root-tree `FREE_SPACE_ITEM` generation and entry counts.
  - Writes the cache generation and per-sector CRC32C checksums into the cache file image.
  - Calls `do_write_file()` to write the cache inode data but deliberately suppresses write failures because the free-space cache is not critical on degraded mounts.
- `update_chunk_caches()`
  - Writes legacy caches for every changed chunk of at least 100 MiB, using a shared batch list.
  - Commits the batch list, then flushes pending partial RAID5/RAID6 stripes for changed parity chunks.

## Free-Space Tree Updating

- `update_chunk_cache_tree()`
  - Copies and merges `space` plus `deleting`, then reconciles `Vcb->space_root` with the merged list.
  - Inserts missing `TYPE_FREE_SPACE_EXTENT` items, leaves matching extent items unchanged, deletes stale extent items, and deletes all bitmap items for the chunk.
  - Inserts remaining merged ranges after the tree walk.
  - Updates an existing `TYPE_FREE_SPACE_INFO` item in place when it has the right size, including parent generation/write metadata, or deletes/reinserts it otherwise.
  - Sets `FREE_SPACE_INFO.count` to the number of extent records and clears flags.
  - Does not emit bitmap items; all output entries are extent items.
- `update_chunk_caches_tree()`
  - Sets `BTRFS_COMPAT_RO_FLAGS_FREE_SPACE_CACHE_VALID`.
  - Walks all chunks under shared `chunk_lock`, updating the free-space tree for chunks whose free space changed.

## Important Dependencies

This file depends on broader WinBtrfs subsystems:

- Tree operations: `find_item`, `find_next_item`, `insert_tree_item`, `delete_tree_item`, `keycmp`
- FCB and inode operations: `open_fcb`, `create_fcb`, `flush_fcb`, `free_fcb`, `reap_fcb`, `mark_fcb_dirty`, `add_fcb_to_subvol`
- Extent operations: `excise_extents`, `insert_extent_chunk`, `get_chunk_from_address`, `protect_superblocks`
- Allocation and chunk state: `alloc_chunk`, `chunk_lock`, `acquire_chunk_lock`, `release_chunk_lock`
- Rollback and batching: `add_rollback`, `clear_rollback`, `do_rollback`, `commit_batch_list`, `clear_batch_list`
- Checksums and time: `calc_crc32c`, `KeQuerySystemTime`, `win_time_to_unix`
- Windows kernel utilities: `ExAllocatePoolWithTag`, `ExFreePool`, `RTL_BITMAP`, `RtlFindFirstRunClear`, `RtlFindNextForwardRunClear`, `ERESOURCE`

## Notable Edge Cases

- Several comments explicitly question behavior when the sector size is not 4096 bytes; both legacy cache loading and allocation have this FIXME.
- Legacy cache bitmap writing is not implemented, and free-space-tree updating deletes bitmap items and rewrites only extent items. Large fragmented free-space maps may therefore serialize less compactly than Linux-generated bitmap-heavy caches.
- `load_stored_free_space_cache()` has a FIXME before bitmap decoding to ensure bitmap reads cannot overflow the cache buffer.
- Legacy cache checksum calculation has FIXME comments for sectors fully inside the checksum area.
- `add_space_entry()` does not merge adjacent ranges; bulk loaders must merge afterward, and callers that skip merging can temporarily have adjacent nodes.
- `space_list_add2()` records rollback for most expansion/insertion cases, but the final contiguous-with-last-entry case grows the last entry without adding rollback state.
- `space_list_add2()` uses `s2->size = length` when a new range envelops an existing entry and extends beyond it; this assumes the new range begins at the adjusted entry start. If there was no left extension, a range starting before or at `s2->address` is handled, but the arithmetic is subtle and should be treated carefully during modification.
- `clear_free_space_cache()` initializes and clears rollback around legacy cache inode deletion, but later free-space-tree deletions are not wrapped in the same rollback path.
- `update_chunk_cache()` ignores cache data write errors by design, so callers may see success even when the legacy cache file was not refreshed.
- Free-space-tree loading trusts the tree structure more than the legacy loader does; it validates item sizes but does not compare parsed free space to chunk usage.
