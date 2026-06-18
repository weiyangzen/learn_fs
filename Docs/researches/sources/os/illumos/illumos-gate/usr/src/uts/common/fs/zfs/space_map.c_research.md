# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/space_map.c

This file implements ZFS space map object encoding, iteration, loading into range trees, append writing, histogram maintenance, truncation, allocation/freeing, incremental destruction, and size estimation.

Key behavior:
- Space map entries can be debug entries, single-word entries, or v2 double-word entries.
- `sm_entry_is_debug()`, `sm_entry_is_single_word()`, and `sm_entry_is_double_word()` classify encoded words.
- `space_map_iterate()` prefetches the requested byte range, walks DMU blocks, decodes non-debug entries, handles double-word entries with vdev IDs, validates alignment and bounds, and invokes a callback.
- `space_map_reversed_last_block_entries()` reads the final block and reverses entries while preserving double-word ordering, supporting safe backward destruction.
- `space_map_incremental_destroy()` destructively processes entries from the tail, invokes a callback, updates allocation accounting inversely as entries are removed, shrinks `smp_length`, and can stop early on callback error such as `EINTR`.
- `space_map_load_length()` and `space_map_load()` reconstruct a range tree by applying alloc/free entries; loading free maps starts with the full space range.
- Histogram functions clear, verify, and add range-tree histograms into the space-map histogram stored in `space_map_phys_t` when the bonus buffer supports it.
- `space_map_write_intro_debug()` appends a debug entry containing action, sync pass, and TXG.
- `space_map_write_seg()` appends one or more encoded entries for a segment, handles block boundaries, pads if a double-word entry would straddle a block, and splits runs by encoding limits.
- `space_map_write_impl()` writes all range-tree segments, choosing double-word entries when spacemap v2 is active and offset/run/vdev ID require it, or optionally for testing.
- `space_map_write()` dirties the header, updates `smp_object` for compatibility, adjusts `smp_alloc`, writes entries, and verifies the source range tree did not change during writing.
- `space_map_open()` allocates an in-core `space_map_t`, holds the bonus buffer, records block size and physical header pointer; `space_map_close()` releases it.
- `space_map_truncate()` either reallocates the object for changed bonus/block/indirect block sizing or frees all ranges in-place, then resets length, allocation, and histogram.
- `space_map_alloc()` allocates a DMU space-map object and increments the histogram feature refcount when enabled.
- `space_map_free_obj()` decrements the histogram feature refcount when appropriate and frees the DMU object.
- `space_map_estimate_optimal_size()` uses range-tree histograms to compute a worst-case encoded size, accounting for single-word versus double-word limits and padding.
- Accessors return object ID, allocated bytes, length, and number of blocks.

Important invariants:
- Space map writes occur in syncing context and caller-provided synchronization is required.
- The append format permits valid zero words, so incremental deletion cannot mark entries as zeroed; it shrinks from the end instead.
- Double-word entries are never split across DMU blocks.
