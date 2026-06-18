# File Research: sources/os/linux/linux-stable/fs/ext4/mballoc.c

## Purpose

Implements ext4's multiblock allocator. It maintains in-memory buddy allocation state derived from on-disk block bitmaps plus preallocation descriptors, chooses allocation groups and free extents, manages inode/locality-group preallocations, updates allocation bitmaps and counters, processes delayed frees after journal commit, supports discard/FITRIM, and exposes free-space iteration for fsmap.

## Main Responsibilities

- Build and maintain per-block-group buddy structures and group free-space summaries.
- Load block bitmaps into the buddy-cache inode and regenerate buddy data from on-disk bitmaps plus preallocations.
- Select allocation groups using allocation criteria, goal hints, optimized xarray indexes, linear fallback, and bitmap prefetching.
- Allocate blocks through `ext4_mb_new_blocks()`, including quota/free-space reservation, preallocation reuse, request normalization, buddy allocation, and bitmap/journal update.
- Track, consume, create, discard, and release inode preallocations and per-CPU locality-group preallocations.
- Free blocks through `ext4_free_blocks()`, with bigalloc cluster rounding, metadata revocation, delayed reuse until journal commit, discard, and buddy/counter updates.
- Initialize and tear down mount-level mballoc state, slab caches, proc/debug sequence views, and KUnit test exports.
- Support fast-commit replay with simple idempotent allocation/free helpers.
- Implement `FITRIM` scanning and `ext4_mballoc_query_range()` free-extent callbacks used by fsmap.

## Key Operations

- `mb_test_bit()`, `mb_set_bit()`, `mb_clear_bit()`, `mb_find_next_zero_bit()`, and `mb_find_next_bit()` wrap ext4 bitmap operations with alignment correction for architectures requiring aligned word access.
- `ext4_mb_generate_buddy()` scans a block-group bitmap for free runs, populates buddy-order counters, records first free cluster and fragment count, validates descriptor free-cluster counts, and updates optimized scan indexes.
- `ext4_mb_init_cache()`, `ext4_mb_init_group()`, and `ext4_mb_load_buddy_gfp()` populate and pin the buddy-cache folios that hold each group's bitmap and buddy block.
- `mb_mark_used()` and `mb_free_blocks()` are the core in-memory state mutators. They update the order bitmaps, `bb_free`, fragment counts, first-free position, largest-free-order index, average-fragment-size index, and optional double-check bitmap.
- `ext4_mb_find_by_goal()`, `ext4_mb_simple_scan_group()`, `ext4_mb_complex_scan_group()`, and `ext4_mb_scan_aligned()` search for goal, power-of-two, general, and stripe-aligned extents.
- `ext4_mb_scan_groups()` dispatches between linear scanning and optimized xarray scanning for `CR_POWER2_ALIGNED`, `CR_GOAL_LEN_FAST`, `CR_BEST_AVAIL_LEN`, `CR_GOAL_LEN_SLOW`, and `CR_ANY_FREE`.
- `ext4_mb_regular_allocator()` coordinates the allocation search, including goal-first search, optimized criteria progression, best-found fallback, and retry with first-free allocation after a lost race.
- `ext4_mb_initialize_context()`, `ext4_mb_group_or_file()`, and `ext4_mb_normalize_request()` construct the allocation context, choose inode vs group preallocation policy, and expand data allocations for locality and future writes.
- `ext4_mb_use_preallocated()` searches inode preallocation rbtrees and locality-group preallocation lists before falling back to buddy allocation.
- `ext4_mb_new_inode_pa()` and `ext4_mb_new_group_pa()` create new preallocation descriptors from oversized successful allocations; `ext4_mb_release_context()` updates consumed group PAs, frees exhausted PAs, drops pinned folios, unlocks locality groups, and records stats.
- `ext4_mb_mark_context()` is the shared bitmap update helper. It reads and optionally journals the bitmap and group descriptor, clears uninitialized bitmap flags, changes bits, updates group/flex counters, recomputes checksums, and optionally syncs buffers.
- `ext4_mb_mark_diskspace_used()` validates selected blocks against filesystem metadata zones, marks them allocated on disk, and decrements the global free-cluster counter.
- `ext4_mb_clear_bb()` and `ext4_free_blocks()` validate free ranges, handle buffer forgetting, round to bigalloc cluster boundaries, clear bitmap bits, defer reuse when the journal requires it, issue discard when appropriate, and update quota/free-cluster accounting.
- `ext4_mb_free_metadata()` stores freed clusters in a per-group rb tree and per-transaction list so metadata/data blocks are not reused until the committing transaction is safe.
- `ext4_process_freed_data()` moves committed freed extents into buddy state and optionally queues discard work.
- `ext4_trim_fs()`, `ext4_trim_all_free()`, and `ext4_try_to_trim_range()` implement FITRIM by marking free extents temporarily used in buddy state while discard I/O is issued.
- `ext4_mballoc_query_range()` loads a group's buddy bitmap and reports free extents through caller-provided callbacks.
- `ext4_mb_new_blocks_simple()` and `ext4_mb_mark_bb()` provide simple replay-time allocation/marking paths for fast commit recovery.

## Dependencies

- Includes `ext4_jbd2.h`, `mballoc.h`, tracepoints, static KUnit stubs, slab/page-cache helpers, block discard APIs, freezer checks, and kernel xarray/list/rbtree facilities.
- Depends on ext4 block bitmap validation/loading from `balloc.c`, group descriptors and counters from ext4 core structures, quota APIs, JBD2 journaling, extent/inode mapping callers, flex_bg counters, fast-commit replay exclusion checks, and mount options.

## Important Invariants

- Buddy state represents on-disk allocated clusters plus currently reserved preallocation clusters; a cluster should not be considered allocatable while any active PA covers it.
- Group lock protects buddy/group-info mutations. PA locks protect descriptor state; inode PA rbtree locks and locality-group locks protect discovery lists.
- Bitmap folios are pinned while selected buddy extents have not yet been committed to on-disk bitmaps, preventing reinitialization from stale disk state.
- Deferred freed metadata is not returned to buddy free space until the relevant journal transaction commits, except for writeback-mode cases with weaker consistency requirements.
- Preallocation deletion is two-phase: mark deleted under PA lock, unlink from group/object lists under the relevant locks, then free immediately or through RCU depending on PA type.
- Bigalloc operations are in cluster units internally and convert to block units at public boundaries.
- Corrupt or inconsistent block-group bitmaps are marked with group corruption flags and avoided by normal allocation scans.

## Research Notes

This is the central allocator for ext4 data and metadata block placement. The file is highly concurrency-sensitive: it deliberately separates on-disk bitmap state, in-core buddy state, and preallocation descriptors, then uses group locks, object locks, PA references, and folio pinning to keep them coherent without serializing all allocation paths. The optimized scan xarrays are performance hints only; allocation remains correct through linear fallback and final group-locked bitmap checks.
