<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/cache_inline.h -->
# sources/storage-engines/wiredtiger/src/include/cache_inline.h

## Purpose
Defines read-side inline helpers for cache usage metrics and session wait eligibility. These functions provide consistent cache-overhead adjustment and aggregate counters for total, ingest, stable, dirty, update, image, and "other" cache usage.

## Important APIs, Types, and Functions
Page-count accessors include `__wt_cache_pages_inuse`, `__wt_cache_pages_inuse_leaf`, `__wt_cache_pages_inuse_ingest`, and `__wt_cache_pages_inuse_stable`.

Byte accessors include `__wt_cache_bytes_plus_overhead`, `__wt_cache_bytes_inuse`, `__wt_cache_bytes_inuse_ingest`, `__wt_cache_bytes_inuse_stable`, `__wt_cache_dirty_inuse`, dirty internal/leaf variants, update byte variants, image byte variants, and `__wt_cache_bytes_other`.

`__wt_session_can_wait` checks whether a session may perform slow operations and excludes sessions ignoring cache size or holding the schema lock.

`__wt_cache_full` compares overhead-adjusted cache bytes in use with the connection cache size.

## Control Flow
Most functions perform relaxed atomic loads from `WT_CACHE`, combine related counters, apply `overhead_pct`, and return the derived value. `__wt_cache_bytes_other` protects against racing counter reads by using `__wt_safe_sub` when subtracting image bytes from total in-memory bytes. `__wt_session_can_wait` is a short flag-gated predicate. `__wt_cache_full` fetches the connection cache and compares in-use bytes to `conn->cache_size`.

## State and Persistence Behavior
The helpers do not mutate state. They read in-memory cache counters and session flags. Their results influence eviction, throttling, block-manager flush decisions, and application backpressure, which indirectly affects when data is reconciled and persisted.

## Dependencies and Integration Points
Depends on `WT_CACHE`, `WT_SESSION_IMPL`, `WT_CONNECTION_IMPL`, atomic load wrappers, `F_ISSET`, lock flag fields, `__wt_safe_sub`, and connection cache size. Integrated with eviction decisions, statistics, cache pressure calculations, block manager behavior, and disaggregated ingest/stable cache accounting.

## Risks and Edge Cases
Relaxed counter reads can observe temporarily inconsistent combinations; callers must treat results as approximate. `overhead_pct` applies uniformly to derived byte categories, so changing that field affects every cache pressure calculation. `__wt_cache_bytes_other` explicitly handles underflow from racing reads; similar external calculations should not subtract raw counters without protection.

## Test Signals
Signals include cache-stat tests for bytes/pages in use, cache overhead configuration tests, eviction-trigger tests around full-cache thresholds, schema-lock/session flag tests for wait eligibility, and concurrent stress tests that ensure derived counters do not underflow or wrap.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/cache_inline.h -->
