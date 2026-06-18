# File Research: sources/os/plan9/9front/sys/src/9/port/page.c

Physical page allocator, free-list manager, and image page-cache support.

Key responsibilities:
- Initializes `palloc.pages` from `conf.mem`, skipping kernel pages and invalid direct-map sentinels.
- Tracks free pages, user page count, and swap high-water/headroom thresholds.
- Allocates pages with color preference in `newpage()`, blocking/kicking pager when low.
- Frees page lists and wakes page waiters in `freepages()`.
- Reclaims unreferenced image-cache pages in `pagereclaim()`.
- Implements page refcount/free helpers: `deadpage()` and `putpage()`.
- Provides `copypage()` and `fillpage()`.
- Maintains image page cache with `cachepage()`, `uncachepage()`, `lookpage()`, and `cachedel()`.
- Clears private pages during panic/sensitive shutdown via `zeroprivatepages()`.

Important behavior:
- `newpage()` can temporarily unlock a caller-provided `QLock` while waiting and returns nil so fault code can retry after relocking.
- `lookpage()` moves found pages to the front of the hash bucket.
- Image-cached pages are not immediately freed by `deadpage()`; their image ref is decremented differently.

Notable risks:
- `zeroprivatepages()` returns early during panic without process context, relying on caller expectations.
- Page initialization assumes `conf.mem` is already stable and correctly excludes kernel ranges.
