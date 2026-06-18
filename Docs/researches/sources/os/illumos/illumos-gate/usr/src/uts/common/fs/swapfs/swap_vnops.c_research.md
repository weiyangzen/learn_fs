# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/swapfs/swap_vnops.c

Swapfs vnode operations for anonymous-memory backing objects, page fault fill, pageout writeback to physical swap slots, large-page support, and page disposal.

Key responsibilities:
- Defines `swap_vnodeops_template` with inactive, getpage, putpage, dispose, and error stubs for unsupported VOPs.
- Implements `swap_getpage()` as a `pvn_getpages()` wrapper around `swap_getapage()`.
- Implements `swap_getapage()` to find/create swapfs pages, optionally force SEGKP pages non-relocatable, read from physical swap backing when present, free physical backing after successful read-in, or zero-fill when no backing exists.
- Implements `swap_getconpage()` for large-page anonymous memory paths using a caller-provided preallocated page, with relocation/size negotiation through `pszc` and `nreloc`.
- Implements `swap_putpage()` to scan vnode page ranges, optionally enqueue async pageout requests, and call `swap_putapage()` for dirty pages.
- Implements `swap_putapage()` to assign physical swap backing via `swap_newphysname()`, cluster adjacent pending async pageout requests when possible, and issue `VOP_PAGEIO()` to the physical swap vnode.
- Implements `swap_dispose()` to route final page disposal to the physical backing vnode when one exists, otherwise to generic `fs_dispose()`.

Dependencies:
- Depends on anonymous/swap metadata helpers: `swap_getphysname`, `swap_newphysname`, `swap_phys_free`, `swap_anon`, and `AH_MUTEX`.
- Uses `sw_getreq`, `sw_putreq`, `sw_putbackreq`, `sw_getfree`, and `sw_putfree` from `swap_subr.c`.
- Uses VM page interfaces: `page_lookup`, `page_create_va`, `page_lookup_create`, `page_relocate_cage`, `pvn_getpages`, `pvn_vplist_dirty`, `pvn_getdirty`, and `pvn_write_done`.
- Uses `segkp` and kernel cage checks for non-relocatable kernel pages.

Concurrency and locking:
- Page locks and page I/O locks drive correctness; functions assert or adjust exclusive/shared page locks as needed.
- Anonymous hash mutexes protect updates that clear `an_pvp/an_poff` after swap-in.
- Async clustering consumes pending requests opportunistically and returns or requeues requests on lookup, dirtiness, allocation, or contiguity failures.

Notable risks:
- `swap_getapage()` frees physical swap backing after reading a page back into memory, marking the page modified; this is central to swap slot lifecycle.
- Async clustering assumes contiguous physical swap slots and same physical vnode; failed clustering must restore page state and requeue correctly.
- `B_FORCE` is stripped in `swap_putpage()` so locked pages are not invalidated.
- `swap_getconpage()` returns special negative values for large-page size negotiation, so callers must distinguish them from normal errno paths.
