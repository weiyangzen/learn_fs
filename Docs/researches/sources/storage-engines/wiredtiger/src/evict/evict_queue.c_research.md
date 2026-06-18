# sources/storage-engines/wiredtiger/src/evict/evict_queue.c

Purpose: manages eviction candidate queues after the tree walk has discovered pages. It sorts candidates by score, trims and counts usable entries, rotates two ordinary queues, maintains the urgent queue indirectly through shared helpers, and lets workers drain queued pages.

Important functions: `__evict_lru_cmp` sorts non-null candidates by eviction score and null entries last; `__evict_lru_cmp_debug` ignores score so debug aggressive mode can test alternate behavior. `__wti_evict_queue_clear_page` and `__wti_evict_queue_clear_page_locked` remove a ref from all queues and clear page LRU flags. `__wti_evict_lru_pages` repeatedly calls `__wti_evict_page`, treating `EBUSY` as a nonfatal candidate failure and waiting when worker queues are empty. `__wti_evict_lru_walk` rotates/fills queues, calls `__wti_evict_walk` to populate entries, sorts and trims them, chooses `evict_candidates`, updates read-generation oldest, records queued clean/dirty/update stats, sets `evict_current`, and signals waiting workers.

Control flow: the eviction server calls `__wti_evict_lru_walk` during a pass when cache pressure exists. The current fill queue alternates with the other ordinary queue; full queues may be skipped unless empty-score pressure is high. After population, candidates are sorted so lower scores and forced-eviction read generations are tried first. Workers call `__wti_evict_lru_pages` to consume candidates through dispatch.

State and persistence behavior: queue state is entirely in memory: candidate arrays, current pointers, candidate/entry counts, page `WT_PAGE_EVICT_LRU` flags, `evict_empty_score`, and `read_gen_oldest`. It does not persist pages itself; it decides which pages will reach `evict_page.c`.

Dependencies and integration points: depends on the eviction walk implementation (`__wti_evict_walk`), dispatch (`__wti_evict_page`), queue helpers from `evict_inline.h`, stats, condition variables, and debug flags. Queue locks must coordinate with urgent insertion in `evict_dispatch.c` and exclusive clearing in `evict_exclusive.c`.

Risks and test signals: queue races can leave page flags set or refs stale. Tests should stress clearing pages while workers drain, both ordinary queues full, empty-score escalation, aggressive mode candidate selection, trimming entries over `WTI_EVICT_WALK_BASE`, null entries from failed walks, worker `WT_NOTFOUND` waits, and stats for queued dirty/update candidates.
