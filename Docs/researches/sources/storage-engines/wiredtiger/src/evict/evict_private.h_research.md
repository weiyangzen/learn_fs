# sources/storage-engines/wiredtiger/src/evict/evict_private.h

Purpose: private eviction subsystem declarations and data structures shared by the eviction implementation files. It defines queue sizing constants, candidate/queue structs, a pass-lock helper macro, and prototypes generated for internal eviction APIs.

Important types and constants: `WTI_EVICT_MAX_TREES`, `WTI_EVICT_WALK_BASE`, and `WTI_EVICT_WALK_INCR` shape how many tree walk points and candidate entries eviction tracks. `WT_EVICT_HAS_WORKERS(session)` tests whether the configured thread group has more than the server thread. `WTI_EVICT_ENTRY` stores a candidate btree, ref, and score. `WTI_EVICT_QUEUE` stores the spinlock, queue array, current pointer, candidate count, entry count, and maximum slot used. `WTI_EVICT_QUEUE_MAX` reserves two ordinary queues plus one urgent queue at `WTI_EVICT_URGENT_QUEUE`. `WTI_WITH_PASS_LOCK` wraps the pass lock with session lock-flag tracking.

Declared APIs: the header exposes queue/candidate functions (`__wti_evict_push_candidate`, `__wti_evict_lru_walk`, `__wti_evict_walk`, queue clearing), dispatch/application functions (`__wti_evict_page`, `__wti_evict_app_assist_worker`), saved-walk/exclusive helpers, handle-list locking, and inline policy functions implemented in `evict_inline.h`.

Control flow and integration: included by `wt_internal.h` consumers inside the eviction subsystem. It is the shared contract between queue production (`evict_lru.c`/walk code outside this item), queue consumption (`evict_dispatch.c`), queue maintenance (`evict_queue.c`), exclusive locking (`evict_exclusive.c`), and server orchestration (`evict_thread.c`).

State and persistence behavior: the structs represent in-memory candidate state only. They indirectly protect persistent page state by ensuring a queued ref is associated with its owning btree and can be locked before reconciliation/discard.

Risks and test signals: struct fields are lock-protected by convention, so misuse can cause races or stale refs. Tests should exercise queue capacity boundaries, urgent queue indexing, worker-count behavior with one versus multiple threads, pass-lock interruption, and generated prototype drift. ABI risk is internal but high because all eviction files agree on these layouts.
