# sources/storage-engines/wiredtiger/src/evict/evict_stat.c

Purpose: gathers detailed per-data-source cache/eviction statistics by walking the in-memory tree. It backs the `cache_walk` diagnostic configuration rather than normal connection-level eviction operation.

Important functions: `__wt_evict_cache_stat_walk` records root and current eviction generation stats, then calls the private `__evict_stat_walk`. `__evict_stat_walk` walks cached refs with `__wt_tree_walk_count` and records page counts, clean/dirty split, internal/leaf split, queued/not-queueable refs, disk-image sizes, memory-only pages, allocation-size anomalies, visited/unvisited age, and read-generation gaps.

Control flow: a stats-enabled session calls `__wt_evict_cache_stat_walk` while positioned on a btree. The walker uses `WT_READ_CACHE | WT_READ_NO_EVICT | WT_READ_INTERNAL_OP | WT_READ_NO_WAIT | WT_READ_VISIBLE_ALL` so it observes cache state without triggering eviction or waiting on unavailable pages. Root stats are read directly from the root page index and root memory footprint.

State and persistence behavior: this file only reads cache/tree/page state and writes data-source statistics. It does not mutate pages or persistent storage. It reads `page->evict_pass_gen`, `page->cache_create_gen`, disk image sizes, queue flags, and page dirty state to infer eviction-walk effectiveness.

Dependencies and integration points: depends on tree walking, page evictability checks, data-source stats macros, btree allocation size, root page index access, and connection eviction generation. It complements `evict_verbose.c`, which prints similar diagnostics to the message stream.

Risks and test signals: diagnostics must avoid blocking or changing cache state. Tests should cover trees with root-only pages, queued pages, dirty/internal/leaf pages, pages without disk images, disk images smaller than allocation size, skipped refs from no-wait walks, and disabled `cache_walk` versus enabled data-source stats. Race tolerance matters because it reads live page and generation values without freezing eviction.
