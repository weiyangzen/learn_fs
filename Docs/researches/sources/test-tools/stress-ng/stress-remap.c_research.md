# sources/test-tools/stress-ng/stress-remap.c

Purpose: implements the `remap` memory/OS stressor for Linux `remap_file_pages()`, repeatedly rearranging pages inside a shared anonymous mapping and verifying that virtual page order changes match the requested layout.

Important APIs/types/functions: `stress_remap_info` exposes `remap-mlock` and `remap-pages` options with `VERIFY_ALWAYS`. `stress_get_unmapped_addr()` reserves and releases an address to later exercise invalid remaps. `remap_order()` applies `remap_file_pages()` page by page, optionally wrapping each page with `mlock()`/`munlock()`. `check_order()` validates sentinel values at the first word of each page.

Control flow: `stress_remap()` resolves page count, forcing a power-of-two fallback when needed, maps the data array and an order array, seeds one marker per page, and optionally locks memory. It prepares one known unmapped address and one mapping with an intentionally unmapped following page for invalid-call coverage. After sync, each loop remaps pages in reverse order, randomized order, all-to-page-zero order, and forward order, checking after every phase. It also calls `remap_file_pages()` on invalid unmapped, out-of-range, flag, and protection combinations.

State and persistence: all state is anonymous shared memory plus optional mapped/unmapped probe ranges. It reports memory usage and mmap statistics, then unmaps all allocations. There is no filesystem persistence.

Dependencies and integration points: requires `HAVE_REMAP_FILE_PAGES` and excludes SPARC. It uses stress-ng memory mapping helpers, mmap stats, random number helpers, sync, settings, and metrics. Unsupported builds return `stress_unimplemented`.

Risks and test signals: `remap_file_pages()` is obsolete and may fail or be unsupported on newer kernels/libcs. Large page counts can hit memory or mlock limits. Verification checks catch incorrect page ordering; metrics report nanoseconds per page remap and mmap residency/dirty/swap/contiguity details.
