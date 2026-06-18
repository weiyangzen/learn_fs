# File Research: sources/os/plan9/plan9/sys/src/9/port/page.c

Implements the physical page allocator, page cache hash, page reference diagnostics, and PTE helpers for the Plan 9 port VM layer.

Key responsibilities:
- `pageinit` builds the global `palloc.pages` array and free list from configured memory banks, assigns cache colors, initializes swap watermarks, and prints memory/swap totals.
- `newpage` allocates a colored page, blocking and kicking the pager when below `swapalloc.highwater`.
- `putpage`, `auxpage`, `pagechainhead`, `pagechaintail`, and `pageunchain` manage the free/LRU list.
- `duppage` opportunistically duplicates image-backed cached pages to preserve cache contents.
- `copypage` copies page contents through temporary kernel mappings.
- `uncachepage`, `cachepage`, `cachedel`, and `lookpage` maintain the image/swap page hash.
- `ptealloc`, `ptecpy`, and `freepte` manage segment PTE tables, including swap references and physical segment free callbacks.
- `checkpagerefs` and `portcountpagerefs` diagnose page reference-count mismatches across process segments.

Important behavior:
- Pages with backing images are returned to the tail; anonymous/swap pages go to the head.
- `newpage` may temporarily release a segment lock during memory pressure to avoid deadlock in page fault paths.
- `lookpage` increments page refs and removes a page from the free list if it was cached but unreferenced.
- `freepte` treats `SG_PHYSICAL` segments specially and uses `pgfree` if supplied.

Cautions:
- `duppage` contains an inline comment describing a suspected race around temporarily putting `np` back on the freelist while copying/caching it.
- Several routines assume specific lock ordering: generally `palloc` before individual `Page`.
