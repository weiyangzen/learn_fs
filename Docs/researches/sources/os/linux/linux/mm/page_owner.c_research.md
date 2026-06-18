# File Research: sources/os/linux/linux/mm/page_owner.c

Page allocation ownership tracker built on `page_ext` and stack depot. When enabled by the early `page_owner` parameter, it records allocation and free stack traces, task identity, GFP mask, order, migration reason, timestamps, and exposes the data through debugfs.

Key responsibilities:
- Defines the `page_owner` page-extension payload and registers `page_owner_ops`.
- Enables tracking through an early boot parameter and initializes stack depot early when requested.
- Records allocation stacks with `__set_page_owner()` and free stacks with `__reset_page_owner()`.
- Maintains stack-record reference counts by base-page count and a linked list of observed stack records for aggregate reporting.
- Marks early allocated pages after page-owner initialization with a dedicated early stack handle.
- Updates owner metadata when pages split, migrate, or copy ownership between folios.
- Prints page-owner details for `dump_page()` diagnostics and `debugfs/page_owner`.
- Exposes aggregate stack reports under `debugfs/page_owner_stacks`, including optional handles, stack traces, page counts, and a count threshold.
- Provides mixed pageblock counting support for `/proc/pagetypeinfo`.

Important behavior:
- Recursion is avoided with `current->in_page_owner` because stack depot and list maintenance can allocate memory.
- Dummy, failure, and early stack handles distinguish recursive capture, failed stack saves, and allocations that predated full tracking.
- Freeing a page clears `PAGE_EXT_OWNER_ALLOCATED` but retains historical owner/free information.
- Migration copies the old owner to the new folio and rewrites old folio handles to preserve stack reference-count balance.
- The debugfs page scanner skips buddy pages, unowned pages, freed pages, and tail PFNs of higher-order allocations.
- Memcg information is included when available, including offline cgroups and slab/objcg cases.

Dependencies:
- Relies on `page_ext`, stack depot, stacktrace capture, debugfs, seq_file, memcg, migration reason names, pageblock migratetypes, local clock timestamps, GFP flag formatting, and page allocator hooks.

Notable risks:
- Stack-record counting is manual because this code does not use the stack depot GET API; refcount balance depends on every allocation/free/migration path.
- Debugfs scans are intentionally lock-light and can miss pages racing with concurrent allocation or free.
- Early allocated page discovery avoids zone lock contention and may skip some pages rather than risk heavy boot-time locking.
