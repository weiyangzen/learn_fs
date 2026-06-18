# File Research: sources/virtualization/spdk/lib/ftl/ftl_l2p_cache.c

## Purpose
Implements the paged/cached L2P backend for large devices with a bounded DRAM resident set.

## Data Model
- L2P is split into 4 KiB pages.
- `l2_mapping` maps L2P page number to durable-format object ID for resident page context.
- Resident pages are allocated from `l2_ctx_pool`, backed by `l1_md` buffers, and tracked with state, update count, pin count, waiters, LRU membership, checkpoint sequence, and IO context.
- Page sets group pin requests that span up to `L2P_MAX_PAGES_TO_PIN` pages.
- Cache state tracks running/shutdown, in-flight IOs, resident/available/evicting pages, deferred page sets, lazy trim work, and management process context.

## Initialization
Creates metadata objects for L2 mapping, page contexts, and resident page buffers. Computes resident-page cap from `conf.l2p_dram_limit`, initializes LRU/deferred lists, restores shared-memory state for fast startup/recovery, and caches the L2P layout bdev/offset/ioch.

## Pin/Get/Set
- Pin requests either pin resident ready pages, queue waiters on pages being loaded, or defer page sets until memory is available.
- Page-in reads one L2P page from metadata storage and wakes queued waiters.
- `get` and `set` require pinned pages, lazily apply trim invalidation if the trim bit is set, promote the page in LRU, and `set` increments page updates.

## Eviction And Persistence
- Eviction chooses cold unpinned ready pages while maintaining a reserve of available pages.
- Dirty pages are written back; clean pages are removed.
- `persist` walks all pages, writes dirty residents, applies trim invalidation, and removes pages.
- `trim` allocates/loads trimmed pages, invalidates entries, writes them out, and clears trim bits.
- `clear` uses metadata clear to initialize persistent L2P to invalid addresses.

## Shutdown
`halt` moves to shutdown and completes only when no page IO and no evictions remain. `process` handles deferred pin page-ins, eviction, and lazy trim while running.

## Dependencies
Uses SPDK bdev IO wait, thread/event/env utilities, FTL core/layout/NV-cache IO/mngt steps, address utilities, mempools, metadata, trim map, and stats.
