# File Research: sources/virtualization/qemu/block/qcow2-cluster.c

## Purpose

Implements qcow2 guest-to-host cluster mapping, L1/L2 table growth and shrink, L2 allocation and copy-on-write, host offset allocation for writes, discard/zero handling, zero-cluster expansion for downgrades, and compressed L2 entry parsing. This is the core qcow2 allocation and mapping engine.

## L1 Table Management

`qcow2_shrink_l1_table()` shrinks the active L1 table:

- Zeroes removed L1 entries on disk.
- Flushes the file.
- Frees now-unreachable L2 table clusters.
- Clears in-memory entries on partial write failure to avoid stale metadata use.

`qcow2_grow_l1_table()` grows the active L1 table:

- Computes exact or expanded target size, with overflow checks.
- Allocates a new aligned in-memory L1 table.
- Allocates new on-disk clusters for the table.
- Flushes refcount cache before writing new metadata.
- Writes the new L1 table in big endian.
- Updates the qcow2 header fields `l1_size` and `l1_table_offset`.
- Switches in-memory state to the new table and frees the old one.
- Rolls back allocations on failure.

`qcow2_write_l1_entry()` writes one aligned group of L1 entries, using request alignment to avoid read-modify-write where possible, and performs active L1 overlap checks.

## L2 Table Loading And Allocation

`l2_load()` loads the correct L2 slice for a guest offset using the L2 table cache. Qcow2 can cache slices rather than entire L2 tables.

`l2_allocate()` creates a new L2 table for an L1 entry:

- Allocates a full L2 table.
- Flushes refcount metadata before using the new table.
- For each cache slice:
  - If no old L2 table exists, initializes the slice to zero.
  - If an old L2 table exists, reads the old slice and copies it.
  - Marks the new slice dirty.
- Flushes the L2 cache so the new L2 table is on disk before publishing it.
- Updates the L1 entry with `QCOW_OFLAG_COPIED`.
- Restores the old L1 entry and frees the new table on failure.

`get_cluster_table()` ensures the relevant L1 entry and L2 table exist and are writable:

- Grows L1 if needed.
- Detects unaligned L2 offsets as corruption.
- Allocates/COWs the L2 table if the L1 entry is not copied.
- Frees the old L2 table after successful COW.
- Returns the cached L2 slice and index.

## Host Offset Lookup

`qcow2_get_host_offset()` maps a guest offset and byte count to a host offset and subcluster type:

- Handles guest offsets beyond L1 size as unallocated.
- Loads the relevant L2 slice.
- Reads L2 entry and optional subcluster bitmap.
- Rejects zero entries in pre-v3 images.
- Rejects compressed clusters when an external data file is used.
- Checks cluster offset alignment.
- For external data files, verifies host cluster offset matches guest cluster offset.
- Uses `count_contiguous_subclusters()` to return the longest range with the same type and contiguous physical layout.
- Returns compressed cluster entries specially, with the L2 entry in `host_offset`.

Supporting helpers:

- `qcow2_get_subcluster_range_type()` counts contiguous subclusters of one type inside an L2 entry.
- `count_contiguous_subclusters()` extends that count across L2 entries while requiring type and physical contiguity.

## Compressed Cluster Allocation

`qcow2_alloc_compressed_cluster_offset()` allocates space for a compressed cluster:

- Does nothing for external data files.
- Ensures target cluster is not already allocated.
- Allocates byte-granular compressed storage with `qcow2_alloc_bytes()`.
- Computes compressed-sector count.
- Encodes compressed flag, offset, and size into the L2 entry.
- Clears subcluster bitmap for extended L2 images.
- Returns the host data offset.

Compressed clusters are never marked copied.

## Copy-On-Write Execution

`perform_cow()` fills unmodified parts of newly allocated clusters before L2 metadata is updated:

- Computes start and end COW regions from `QCowL2Meta`.
- May merge start and end reads when the skipped middle region is small.
- Temporarily releases `s->lock` while doing I/O.
- Reads old data directly through the driver callback to avoid double throttling and request tracking.
- Encrypts copied regions when the image is encrypted.
- Writes copied regions and optional guest data to the new allocation.
- Marks the L2 cache as depending on a protocol flush if the write succeeds.

`do_perform_cow_read()` and `do_perform_cow_write()` wrap the actual I/O and overlap checks.

## Linking Allocations Into L2

`qcow2_alloc_cluster_link_l2()` publishes newly allocated clusters:

- Allocates an array for old overwritten L2 entries.
- Performs required COW.
- Marks image dirty for lazy refcounts.
- Makes the L2 cache depend on the refcount cache when accurate refcounts are required.
- Loads the relevant L2 slice and marks it dirty.
- Writes new L2 entries with `QCOW_OFLAG_COPIED`.
- Updates extended L2 subcluster allocation/zero bitmaps for the written range.
- Frees old clusters after the new L2 entries are in place, unless `keep_old_clusters` is set.

`qcow2_alloc_cluster_abort()` frees allocated clusters when a request fails before L2 linking.

## L2 Metadata Planning

`calculate_l2_meta()` creates `QCowL2Meta` records for write requests that need COW or L2 updates:

- Checks all affected subclusters for invalid entries.
- Determines whether COW can be skipped when overwriting already normal allocated clusters.
- Computes leading and trailing COW ranges based on cluster type, subcluster bitmaps, compression, zero state, and whether the old cluster is kept.
- Inserts the metadata into `s->cluster_allocs` so concurrent requests can detect dependencies.

This function is the bridge between allocation planning and later metadata publication.

## Write Allocation Path

`qcow2_alloc_host_offset()` is the main allocator for write requests:

- Starts with a guest offset and requested byte count.
- Builds a contiguous host range, potentially shorter than requested.
- Handles in-flight allocation dependencies through `handle_dependencies()`.
- Reuses copied clusters with `handle_copied()`.
- Allocates new clusters with `handle_alloc()` when needed.
- Returns a host offset and adjusted byte count.
- Returns a linked list of `QCowL2Meta` records for the caller to commit or abort.

Supporting pieces:

- `cluster_needs_new_alloc()` classifies whether an L2 entry requires new storage.
- `count_single_write_clusters()` counts contiguous entries that are either reusable or need new allocation.
- `handle_dependencies()` checks overlap with in-flight `QCowL2Meta` requests, shortens the current request where possible, or waits and asks the caller to restart with `-EAGAIN`.
- `qcow2_wait_for_dependencies()` waits for conflicting in-flight allocations for discard/zero paths.
- `handle_copied()` finds already allocated copied clusters that can be written in place and may create metadata for subcluster state changes.
- `do_alloc_cluster_offset()` performs actual allocation, either in the qcow2 file or at the matching guest offset for external data files.
- `handle_alloc()` counts allocatable/COW clusters, allocates storage, adjusts byte counts, and creates L2 metadata.

## Discard Handling

`qcow2_cluster_discard()` discards a cluster-aligned range:

- Waits for conflicting in-flight allocations.
- Iterates by L2 slice.
- Sets `s->cache_discards` while batching discard work.
- Calls `discard_in_l2_slice()` for each slice.
- Processes queued discards after success/failure.

`discard_in_l2_slice()` updates L2 entries for each cluster:

- For full discard, clears the L2 entry/bitmap so reads can fall through to backing.
- For normal discard, preserves zero-read semantics where possible.
- Handles v3 zero flags, extended L2 zero bitmaps, backing-file behavior, and `discard_no_unref`.
- Frees old clusters unless references are intentionally kept.
- Passes discard requests through even when references are kept.

## Zeroing

`qcow2_subcluster_zeroize()` zeroes a subcluster-aligned range:

- Waits for allocation dependencies.
- For raw external data files, writes zeroes to the external data file first.
- For qcow2 v2:
  - Uses discard when no backing file exists.
  - Otherwise returns unsupported because v2 lacks zero flags.
- Splits the range into head partial cluster, full clusters, and tail partial cluster.
- Uses `zero_l2_subclusters()` for partial clusters in extended L2 images.
- Uses `zero_in_l2_slice()` for full clusters.

`zero_in_l2_slice()` marks whole clusters as zero:

- May unmap allocated or compressed clusters.
- Honors `BDRV_REQ_MAY_UNMAP` and `discard_no_unref`.
- Sets extended L2 zero bitmaps or classic `QCOW_OFLAG_ZERO`.
- Frees or discards old clusters if unmapping.

`zero_l2_subclusters()` marks a subset of subclusters zero in the L2 bitmap and rejects partial zeroing of compressed clusters.

## Zero Cluster Expansion

`qcow2_expand_zero_clusters()` prepares images for downgrade to formats that do not support zero clusters:

- Processes the active L1 table.
- Empties the L2 cache before directly modifying inactive snapshot L2 tables.
- Processes each snapshot L1 table.

`expand_zero_clusters_in_l1()` walks L1/L2 metadata:

- Rejects images with subclusters.
- For zero-plain clusters:
  - If there is no backing file, deallocates them.
  - If backed, allocates real clusters and writes zeroes.
- For zero-allocated clusters, writes zeroes to the data file and converts entries to normal allocated entries.
- Preserves sharing semantics by checking L2 refcount and adjusting new cluster refcount when needed.
- Handles active L2 tables through the cache and inactive L2 tables through direct disk I/O.
- Emits progress callbacks by L1 entry.

## Compressed Entry Parsing

`qcow2_parse_compressed_l2_entry()` decodes a compressed L2 entry into:

- Compressed data offset.
- Compressed byte size, derived from compressed-sector count and sector alignment.

It asserts that the entry is actually compressed.

## Error And Consistency Model

The cluster code protects qcow2 metadata with several recurring rules:

- Metadata offsets must be cluster-aligned unless encoded compressed data allows byte granularity.
- L2 tables are flushed before L1 entries publish them.
- Refcount updates and data/COW writes are ordered before L2 updates through cache dependencies.
- Overlap checks precede direct metadata/data writes.
- Old clusters are freed only after replacement metadata is installed.
- In-flight allocations are tracked to serialize overlapping COW and metadata updates.
- External data files require host offsets to match guest offsets and disallow compressed clusters.
- Pre-v3 images cannot contain zero-cluster entries.

## Interactions

This file is tightly coupled to:

- `qcow2-cache.c` for L2 cache get/put/dirty/flush/dependency operations.
- qcow2 refcount allocation/free functions.
- qcow2 overlap checking and corruption signaling.
- Block layer coroutine I/O APIs.
- Dirty/lazy refcount state.
- Extended L2 subcluster helpers from qcow2 headers.
- Snapshot metadata when expanding zero clusters.
