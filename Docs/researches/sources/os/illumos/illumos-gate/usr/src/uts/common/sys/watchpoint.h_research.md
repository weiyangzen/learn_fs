# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/watchpoint.h

`watchpoint.h` defines the VM-side data structures and kernel helper APIs for process watchpoints. The user-facing watchpoint interface is in `proc(5)` and `sys/procfs.h`; this header describes how the kernel represents watched ranges and the pages whose protections are modified to detect access.

`watched_area_t` represents one watched virtual-address interval. It is stored in an AVL tree sorted by user virtual address and records start address, end address, and watch type flags. `watched_page_t` represents one affected page, also AVL-linked and additionally linked into the process protection list. It stores the page address, modified and original protections, reference counts for user/kernel `pr_mappage()` mappings by access class, flags, and counts of read/write/execute watched areas intersecting the page.

Page flags distinguish pages whose watch protections are temporarily restored (`WP_NOWATCH`) from pages that need a `SEGOP_SETPROT()` update (`WP_SETPROT`).

Kernel helpers include copy and word-access variants that ignore watchpoints, region-scoped disable/enable functions for copyops, thread-wide watchpoint enable/disable, global setup, predicates for watch pages and watchpoints, single-step watch handling, AVL comparators, and `watch_copyops`. `pr_find_watched_area()` supports lookup/insertion-position discovery in a process watch-area tree.

Correctness depends on carefully bracketing temporary disables and restoring protections after kernel copies; otherwise kernel-internal accesses could spuriously trigger user watchpoints or leave watched pages unprotected.
