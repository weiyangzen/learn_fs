# File Research: sources/virtualization/qemu/block/qcow2-bitmap.c

## Purpose

Implements qcow2 persistent dirty bitmap support. It serializes QEMU `BdrvDirtyBitmap` objects into the qcow2 bitmap extension, loads them back on open, reports bitmap metadata, removes persistent bitmaps, and handles read-only/read-write reopen transitions. The file is specifically responsible for the on-disk bitmap directory, bitmap tables, bitmap data clusters, and the consistency protocol using the `IN_USE` and `AUTO` flags.

## Main Data Structures

- `Qcow2BitmapDirEntry`: packed on-disk bitmap directory entry. Contains bitmap table offset/size, flags, type, granularity, name length, and extra-data length.
- `Qcow2BitmapTable`: in-memory description of an on-disk bitmap table: offset and number of 64-bit entries.
- `Qcow2Bitmap`: in-memory list item combining table metadata, flags, granularity, name, and optional `BdrvDirtyBitmap *`.
- `Qcow2BitmapList`: simple queue of `Qcow2Bitmap`.
- `BitmapType`: currently only `BT_DIRTY_TRACKING_BITMAP = 1`.

## Format Limits And Validation

The file defines the qcow2 bitmap extension constraints:

- Maximum bitmap table entries: `BME_MAX_TABLE_SIZE`.
- Maximum physical bitmap size in RAM: `BME_MAX_PHYS_SIZE`.
- Granularity bounds: 2^9 through 2^31.
- Maximum bitmap name size equals `BDRV_BITMAP_MAX_NAME_SIZE`.
- Directory reserved flags are rejected with `BME_RESERVED_FLAGS`.
- Table entry reserved bits are rejected with `BME_TABLE_ENTRY_RESERVED_MASK`.
- Table entries either point to cluster-aligned data clusters or encode an all-ones optimization with `BME_TABLE_ENTRY_FLAG_ALL_ONES`.

Important validators:

- `check_table_entry()` rejects reserved bits, illegal all-ones use with nonzero offsets, and unaligned data offsets.
- `check_constraints_on_bitmap()` validates image length, granularity, computed serialized size, and name length for a bitmap to be stored.
- `check_dir_entry()` validates directory entry fields, type, flags, table bounds, cluster alignment, physical bitmap size, and whether the stored table is large enough for the current virtual image length when the bitmap is valid.

## Bitmap Table And Data I/O

- `bitmap_table_load()` reads a bitmap table from disk, converts entries from big endian, and validates every entry.
- `clear_bitmap_table()` frees all data clusters referenced by a bitmap table and clears their table entries.
- `free_bitmap_clusters()` loads a table, frees all referenced bitmap data clusters, frees the table cluster range, and clears the in-memory table metadata.
- `load_bitmap_data()` deserializes bitmap content from the table into a `BdrvDirtyBitmap`.
  - Empty table entries deserialize as zero ranges.
  - Entries with `BME_TABLE_ENTRY_FLAG_ALL_ONES` deserialize as all-dirty ranges.
  - Nonzero offsets are read from disk cluster by cluster.
- `store_bitmap_data()` allocates one qcow2 cluster for each serialized dirty bitmap cluster that actually contains dirty bits, writes serialized data clusters, and builds the bitmap table.
- `store_bitmap()` writes the bitmap table itself, after storing bitmap data, then records the resulting table offset and size.

## Bitmap Directory Handling

The bitmap directory is loaded and stored through a private list abstraction:

- `bitmap_list_load()` reads the directory, converts each entry to CPU endian, validates structure and constraints, rejects unsupported extra data, enforces the header bitmap count, and builds a `Qcow2BitmapList`.
- `bitmap_list_store()` calculates directory size, writes directory entries in big-endian format, and either updates in place or allocates a new directory.
- `bitmap_directory_to_be()` walks the variable-length directory entries and endian-swaps each entry.
- Helper functions calculate entry size, locate names, copy names, and advance to the next directory entry.

This file treats directory corruption conservatively. Mismatched counts, unsupported extra data, invalid constraints, and malformed variable-length entries fail load and can increment check corruption counters.

## Header Update Protocol

Persistent bitmap metadata is protected by the qcow2 autoclear bitmap feature bit:

- `update_header_sync()` updates the qcow2 header and flushes the protocol file.
- `update_ext_header_and_dir_in_place()` clears `QCOW2_AUTOCLEAR_BITMAPS`, flushes the header, updates the existing directory in place, flushes again, then restores the autoclear bit and flushes. This is used for safe `IN_USE` flag updates where the directory size and bitmap count are unchanged.
- `update_ext_header_and_dir()` allocates and writes a new bitmap directory when the set of bitmaps changes, updates header fields, flushes caches/header, and frees the old directory after success. On failure it frees newly allocated directory clusters and restores the old in-memory header state.

The ordering is central: if an update fails while autoclear is cleared, older QEMU versions or repair tools can discard leaked or inconsistent bitmap metadata safely.

## Loading Persistent Bitmaps

`qcow2_load_dirty_bitmaps()` is called during image open/invalidation:

- If no bitmap extension exists, it returns success immediately.
- Loads the bitmap directory.
- For each bitmap:
  - If the bitmap is marked `IN_USE` and a matching RAM bitmap already exists, it skips loading, supporting shared-storage migration cases.
  - Otherwise creates a dirty bitmap with the stored granularity and name.
  - If `IN_USE` is set, it does not trust the on-disk contents and marks the RAM bitmap inconsistent.
  - If `IN_USE` is clear, it loads bitmap data and then marks the directory entry `IN_USE` so the bitmap is protected while QEMU controls it.
  - If `AUTO` is clear, it disables the bitmap.
- If any `IN_USE` flags must be set and the image can be written, it updates the directory in place.
- If the image cannot be written, created bitmaps become read-only.

Failure releases any bitmaps created during that load attempt.

## Reporting Bitmap Info

`qcow2_get_bitmap_info_list()` loads the bitmap directory and returns QAPI bitmap info objects with:

- Name.
- Granularity.
- User-visible flags derived from `BME_FLAG_IN_USE` and `BME_FLAG_AUTO`.

## Reopen Transitions

`qcow2_reopen_bitmaps_rw()` handles read-only to read-write behavior:

- Loads the directory and matches each stored bitmap to an in-memory bitmap.
- If an on-disk bitmap is not marked `IN_USE`, its RAM bitmap must be read-only and consistent; then the directory is updated to set `IN_USE`.
- If an on-disk bitmap is already `IN_USE`, read-only consistent RAM state is treated as suspicious and rejected.
- After successful directory updates, previously read-only RAM bitmaps are made writable.

`qcow2_reopen_bitmaps_ro()` stores persistent dirty bitmaps without releasing them, then marks persistent RAM bitmaps read-only.

## Storing Persistent Bitmaps

`qcow2_store_persistent_dirty_bitmaps()` is the main persistence writer:

- Loads the current bitmap list or creates an empty one.
- Iterates all block dirty bitmaps.
- Skips nonpersistent and inconsistent bitmaps.
- Keeps read-only persistent bitmaps without rewriting data, but associates them with existing directory entries so they may be released if requested.
- For writable persistent bitmaps:
  - Validates constraints.
  - Adds new directory entries as needed.
  - For existing entries, requires the old entry to be `IN_USE`; old table metadata is queued for freeing after success.
  - Stores data clusters and table clusters.
- Updates the bitmap extension directory/header.
- Frees old bitmap tables only after the new directory has been committed.
- On failure, frees newly written bitmap data/table clusters and leaves old tables intact.

The `release_stored` option is used by inactivation/close/migration flows to release RAM bitmaps after successful store.

## Removal And Resize Checks

`qcow2_co_remove_persistent_dirty_bitmap()` removes a named persistent bitmap:

- If no bitmap extension or no matching bitmap exists, it succeeds.
- Holds `s->lock`, loads the bitmap list, removes the entry, updates extension header/directory, then frees the removed bitmap clusters.

`qcow2_truncate_bitmaps_check()` ensures persistent bitmaps can tolerate image resize:

- All persistent bitmaps must be loaded into RAM.
- Each must pass normal dirty bitmap checks, including not being inconsistent.

## Creation Capability And Size Estimation

`qcow2_co_can_store_new_dirty_bitmap()` checks whether a new persistent bitmap can be created:

- Rejects duplicate names.
- Requires qcow2 v3 or later because v2 lacks autoclear feature support.
- Checks bitmap constraints.
- Checks maximum bitmap count and bitmap directory size.

`qcow2_supports_persistent_dirty_bitmap()` returns whether the image version supports persistent dirty bitmaps.

`qcow2_get_persistent_dirty_bitmap_size()` estimates space needed to copy persistent bitmaps into an image with a given cluster size, including worst-case bitmap data, bitmap table entries, and directory contribution.

## Error And Consistency Model

The file consistently separates unsafe/inconsistent states from valid bitmap contents:

- `IN_USE` means the on-disk bitmap data may be stale or under active ownership.
- Cleanly stored bitmaps clear `IN_USE`; loading writable images sets it again before exposing mutable RAM state.
- Directory/header updates use autoclear ordering to avoid leaving metadata that unsupported readers would preserve incorrectly.
- Old bitmap clusters are freed only after a new directory is durable enough to reference replacement metadata.
- Validation rejects malformed directory and table inputs before bitmap data is trusted.

## Interactions

This file depends heavily on:

- `block/dirty-bitmap.h` serialization/deserialization APIs.
- qcow2 allocation/free helpers such as `qcow2_alloc_clusters()` and `qcow2_free_clusters()`.
- overlap checks via `qcow2_pre_write_overlap_check()`.
- header updates via `qcow2_update_header()`.
- qcow2 state fields: bitmap directory offset/size, bitmap count, autoclear flags, version, cluster size, and lock.
