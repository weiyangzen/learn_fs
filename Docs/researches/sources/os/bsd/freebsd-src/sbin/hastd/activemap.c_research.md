# File Research: sources/os/bsd/freebsd-src/sbin/hastd/activemap.c

`activemap.c` implements HAST dirty-extent tracking for replication and resynchronization.

Key behavior:
- Tracks extents over a media range using:
  - `am_memtab`: pending write/reference count per extent.
  - `am_memmap`: in-memory dirty bitmap.
  - `am_diskmap`: bitmap image intended for disk.
  - `am_syncmap`: extents needing synchronization.
  - `am_keepdirty`: LRU-ish list of recently dirty extents kept dirty to reduce bitmap updates.
- `activemap_init()` validates power-of-two extent/sector sizes, computes extent count, bitmap sizes, and allocates all maps.
- `activemap_write_start()` marks extents dirty before writes and reports when disk metadata should be updated.
- `activemap_write_complete()` decrements pending writes and cleans extents when no pending writes remain and they are not kept dirty.
- `activemap_extent_complete()` clears dirty state after a sync extent’s expected requests complete.
- `activemap_copyin()` loads an on-disk bitmap and initializes pending request counts for dirty extents.
- `activemap_merge()` merges a remote dirty bitmap into local sync state.
- `activemap_bitmap()` materializes the disk bitmap from memory and overlays keep-dirty extents.
- `activemap_sync_offset()` iterates dirty extents in `MAXPHYS` chunks for resync work and returns completed extent IDs through `syncextp`.
- `activemap_need_sync()` marks extents for synchronization when a component is unavailable.
- `activemap_calc_ondisk_size()` computes the rounded bitmap storage size without creating a map.
- `activemap_dump()` prints memory/disk/sync bitmaps for diagnostics.

Important details:
- Extent size must be a power of two; `bitcount32(extentsize - 1)` derives the shift.
- Last extents shorter than full extent size are handled by `ext2reqs()` and `activemap_sync_offset()`.
- The keep-dirty cache can intentionally leave disk bitmap bits set even after memory writes complete.
