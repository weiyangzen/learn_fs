# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_indirect_mapping.c

## Purpose
Implements the in-memory and on-disk handling for ZFS indirect vdev mapping objects used after device removal. The mapping translates source offsets on a removed vdev to destination DVAs elsewhere in the pool and optionally tracks obsolete byte counts per mapping entry.

## Main Responsibilities
- Validate mapping handles with `vdev_indirect_mapping_verify()`, including object/dbuf/phys consistency, entry-array presence, max-offset bounds, and obsolete-count object expectations.
- Provide accessors for entry count, max offset, DMU object id, bytes mapped, and logical mapping-array byte size.
- Locate mapping entries by source offset using a custom binary search over sorted mapping entries.
- Allocate, open, close, and free DMU objects containing the mapping and optional obsolete-count arrays.
- Append new mapping entries in syncing context and maintain the in-core entry array.
- Load and update obsolete counts from the obsolete spacemap.

## Key Functions
- `dva_mapping_overlap_compare()` treats entries as half-open ranges `[src, src + asize)`, returning less/equal/greater relative to an offset.
- `vdev_indirect_mapping_entry_for_offset_impl()` performs binary search and optionally returns the next greater mapping entry when an exact overlap is missing.
- `vdev_indirect_mapping_alloc()` creates the main DMU metadata object; when `SPA_FEATURE_OBSOLETE_COUNTS` is enabled it allocates a parallel uint32 counts object and increments the feature refcount.
- `vdev_indirect_mapping_open()` holds the bonus buffer, detects the newer bonus layout by bonus size, and reads all physical entries into memory.
- `vdev_indirect_mapping_add_entries()` consumes a list of `vdev_indirect_mapping_entry_t`, writes entries and obsolete counts in `SPA_OLD_MAXBLOCKSIZE` batches, updates `vimp_bytes_mapped`, `vimp_max_offset`, and `vimp_num_entries`, then rebuilds the in-memory array.
- `vdev_indirect_mapping_increment_obsolete_count()` walks mapping entries covering a logical range and increments per-entry byte counts, asserting counts never exceed entry size.
- `vdev_indirect_mapping_load_obsolete_spacemap()` iterates a spacemap and applies obsolete allocations to the count array.

## Important Behavior And Invariants
- Mapping entries must be appended in nondecreasing source-offset order; `vdev_indirect_mapping_add_entries()` asserts each new `src_offset` is at or beyond the current max offset.
- Fully obsolete entries should not be added; entry obsolete count must be less than mapped size.
- Obsolete counts are optional for old-format mappings. If absent, loading counts returns a zeroed array.
- The size accessor deliberately avoids full verification so stats paths can read a possibly stale entry count without contending with concurrent changes.

## Dependencies
Uses DMU object APIs, DMU bonus buffers, SPA feature flags, `space_map_iterate()`, ZIO buffers, and DVA mapping macros from ZFS vdev headers.
