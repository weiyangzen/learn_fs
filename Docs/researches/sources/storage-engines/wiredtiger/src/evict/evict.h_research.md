# sources/storage-engines/wiredtiger/src/evict/evict.h

## Purpose
Defines the public internal eviction subsystem state structure, flags, exported eviction APIs, and inline helper prototypes for WiredTiger cache eviction.

## Important APIs, types, and fields
`struct __wt_evict` tracks eviction progress, application waits/evictions, max page sizes per checkpoint, max eviction latency, nested history-store eviction time, lock wait time, read generations, eviction pass generations, condition variables/spinlocks, dirty/clean/update trigger and target percentages, checkpoint/scrub targets, cache wait/stuck timeouts, tuning data, LRU walk state, eviction queues, pass interruption, eviction slots, aggression score, empty-queue score, cache flags, and tuning/use-NPOS booleans. Defines include pressure/aggression constants, cache state flags (`WT_EVICT_CACHE_*`), call flags (`WT_EVICT_CALL_*`), `WT_EVICT_MAX_WORKERS`, and prototypes for eviction create/destroy/config, eviction calls, file eviction, exclusive file eviction, worker thread lifecycle, stats, verbose dump, priority, server wake, and many static inline helpers.

## Control flow and state model
The header is not executable control flow but establishes the shared state contract consumed by eviction server, worker, application-assist, checkpoint, cache accounting, and page-management code. The queue pointers (`current`, `fill`, `other`, `urgent`) model double-buffered LRU candidate queues plus urgent eviction. Progress and aggression counters determine when eviction becomes more forceful or declares the cache stuck. Threshold fields separate clean, dirty, update, hard, checkpoint, and scrub pressure.

## Persistence, dependencies, and integration
Eviction state is in-memory connection/cache state, not durable data, but it drives when dirty pages are written and pages leave cache. It includes `evict_private.h` and depends on core WiredTiger types such as `WT_SESSION_IMPL`, `WT_REF`, `WT_PAGE`, `WT_BTREE`, `WT_CACHE_OP`, locks, condition variables, and queue definitions. Generated prototype sections are maintained by `prototypes.py`.

## Risks and test signals
Risks are race conditions on shared counters/flags, threshold misconfiguration, queue pointer invariants, worker tuning instability, stuck-cache false positives/negatives, and prototype drift if generated sections are edited manually. Tests/signals include cache pressure workloads, dirty/update-heavy workloads, checkpoint scrub behavior, urgent eviction, application assist, worker scaling, exclusive file eviction, in-memory and history-store reentry scenarios, stats accuracy, and generated-prototype verification.
