# sources/storage-engines/wiredtiger/src/btree/bt_read.c

## Purpose

`bt_read.c` implements btree page acquisition: converting disk/deleted/memory/locked/split `WT_REF` states into a usable in-memory page with proper hazard-pointer protection. It handles disk reads, page-delta reconstruction, shared disk-image cache interaction, fast-delete instantiation, eviction assistance, forced eviction of oversized pages, and read statistics. The complete 819-line source was read.

## Important APIs, Types, and Functions

`__wt_page_in_func` is the exported page-in loop. `__page_read` locks disk/deleted refs, reads or reconstructs page images, builds in-memory pages, instantiates updates, handles fast-delete state, and publishes `WT_REF_MEM`. `__page_read_build_full_disk_image` merges base pages with delta chains for internal and leaf pages. `__evict_force_check` and `__wt_page_release_evict` decide and perform urgent eviction/splitting of oversized modified leaf pages.

## Control Flow

`__wt_page_in_func` loops on `WT_REF` state. Deleted refs may be skipped or read; disk refs are read unless cache-only flags forbid I/O; locked refs stall or return not-found for no-wait callers; split refs return `WT_RESTART`; memory refs acquire a hazard pointer and may trigger forced eviction before returning.

`__page_read` CAS-locks the ref, sets `WT_REF_FLAG_READING` for normal disk reads, creates fresh pages for addressless deleted refs, and may avoid reading globally visible fast-deleted pages. It then uses the shared disk cache or `__wt_blkcache_read_multi`. Multi-item reads are reconstructed from deltas, optionally verified in diagnostic builds, and instantiated with `__wti_page_inmem`. It copies disaggregated block metadata, instantiates updates, handles page-delete state, tracks page history, clears reading state, and sets `WT_REF_MEM`. Error paths restore state and free owned buffers.

## State and Persistence Behavior

The file owns `WT_REF` state transitions during reads and updates flags such as `WT_REF_FLAG_READING`, `WT_PAGE_EVICT_NO_PROGRESS`, and `WT_PAGE_PREFETCH`. It does not write btree contents, but it may store disk images in the shared disk cache and may instantiate fast-delete pages with `modify->instantiated`, which affects later reconciliation. It also preserves disaggregated storage LSN/block metadata on in-memory pages.

## Dependencies and Integration Points

Dependencies include block cache reads, shared disk cache, page image parsing, update instantiation, fast-delete visibility, transaction oldest updates, eviction assistance, urgent eviction, hazard pointers, page history tracking, delta reconstruction, diagnostic verification, and statistics.

## Risks and Edge Cases

Correctness depends on ref-state CAS ordering, `WT_REF_FLAG_READING`, and hazard-pointer release/acquire behavior. Delta reconstruction and shared-cache ownership are buffer-lifetime sensitive. Fast-delete optimization is disabled for salvage, verify, and disaggregated btrees because those modes need original page details. Forced eviction must avoid checkpoint, no-reconcile, history-store, ingest, and transaction-resolution cases that can stall or corrupt semantics.

## Test Signals

Cover disk/deleted/page-cache reads, no-wait and cache-only reads, skip-deleted reads, split restarts, fast-delete visible and invisible cases, disaggregated pages, shared disk-cache hit/collision/insert paths, delta reconstruction for leaf/internal pages, cleanup after read failures, locked-ref waiting, and forced eviction of oversized modified pages.
