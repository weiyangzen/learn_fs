# sources/storage-engines/wiredtiger/src/btree/bt_prefetch.c

Purpose: implements B-tree prefetch queuing and worker-side page-in for pages likely to be read soon. It attempts to warm the block cache/cache with nearby leaf pages while avoiding repeated prefetch from the same parent and avoiding disk reads in unsuitable states.

Important APIs/types/functions: `__wti_btree_prefetch` scans sibling refs under a parent and queues disk leaf pages. `__wt_prefetch_page_in` runs from a prefetch queue entry and performs the actual page read/release side effect. It uses session prefetch state (`session->pf`), `WT_PREFETCH_QUEUE_ENTRY`, connection prefetch queue counters, ref flags, and split-generation protection.

Control flow: prefetch first verifies it can safely traverse the parent page: leaf refs are allowed, otherwise the session must already be in a split generation. It suppresses repeated prefetches from the same parent until enough skips have occurred. It then scans `ref->home` children and, while queue capacity and per-trigger limits allow, queues refs that are disk-resident leaf pages, not fast-deleted, and not already flagged for prefetch. The worker validates the dhandle/ref, skips refs no longer on disk, enters the split generation, copies the ref address, calls `__wt_page_in` with `WT_READ_PREFETCH | WT_READ_SKIP_DELETED`, releases the page, and leaves the generation.

State and persistence behavior: no persistent data changes. Runtime state includes setting/observing prefetch flags through the queue, session bookkeeping for previous parent and skip count, queue depth, page reads into cache, immediate hazard release, and prefetch success/failure/skip statistics.

Dependencies and integration points: integrates with cursor/read path prefetch triggers, connection prefetch queue, page-in/page-release, split-generation safety, ref state flags, fast-delete visibility skipping, dhandle lifetime management, and stats/verbose logging.

Risks: scanning an internal page without split-generation protection can race with splits. Queueing the same parent repeatedly can waste work; the skip counter throttles this. Queued refs may move to another parent or leave disk state before the worker runs, so the worker revalidates. Fast-deleted pages are skipped to avoid warming data readers can ignore.

Test signals: queue capacity and per-trigger limits, same-parent throttling, split-generation skip for unsafe internal traversal, worker handling of changed home refs, no-valid-dhandle/internal-page assertions, refs no longer on disk, deleted-page skipping, page read/release side effects, and stats for queued/read/fail/skipped pages.
