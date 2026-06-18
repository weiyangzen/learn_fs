# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/watchpoint.c

Kernel implementation of procfs-style user watchpoints. It modifies page protections for watched areas, detects watchpoint faults, coordinates trap-before/trap-after delivery, and installs copy-operation wrappers so kernel copy paths honor user watchpoints during system calls.

Key elements:
- `watch_copyops` replaces normal thread copy operations with watch-aware `copyin`, `copyout`, string copy, `fuword`, `suword`, and `physio` wrappers.
- `pr_do_mappage()` is the core protection remapping routine. It walks `as->a_wpage`, reference-counts temporary map-ins per watched page, sets `WP_NOWATCH`, updates segment protections through `SEGOP_SETPROT`, and coordinates with `holdwatch()`/`continuelwps()` through `p_maplock` and `p_mapcnt`.
- `setallwatch()` reapplies watch protections after a stopped LWP resumes and frees `watched_page` records whose watched area counts dropped to zero.
- `pr_is_watchpage_as()` / `pr_is_watchpage()` test whether a virtual address falls on a page whose current protections were reduced for watchpoint handling.
- `pr_is_watchpoint()` checks `p->p_warea` AVL ranges for read, write, or execute watchpoint overlap and returns the trap code plus trap-after and length metadata.
- `do_watch_step()` temporarily maps a watched page, enables single-step with `prstep()`, and records the pending trap-after state in `lwp_watch`.
- `undo_watch_step()` reverses trap-after single-step state, unmaps any temporary page mappings, and fills `k_siginfo_t` for `SIGTRAP`/`FLTWATCH` if needed.
- `sys_watchpoint()` handles watchpoints hit inside system-call copy paths: it can stop for `FLTWATCH`, post `SIGTRAP`, temporarily mask other signals, and reports whether a debugger cleared the condition.
- `watch_xcopyin()`, `watch_xcopyout()`, `watch_copyinstr()`, and `watch_copyoutstr()` split operations by page and watched-area boundaries, temporarily restore access through `pr_mappage()`, perform `_noerr` copies under `on_fault()`, and invoke `sys_watchpoint()` at the right point for trap-before/trap-after.
- `watch_fuword*()` and `watch_suword*()` provide scalar load/store variants with the same watchpoint semantics.
- `watch_physio()` splits multi-iovec physical I/O so each user iovec can be checked and temporarily mapped separately.
- `wa_compare()`, `wp_compare()`, and `pr_find_watched_area()` provide AVL ordering and overlap lookup helpers for watched areas/pages.
- `watch_enable()` / `watch_disable()` install or remove the watch copyops on a thread and toggle `TP_WATCHPT`.
- `copyin_nowatch()`, `copyout_nowatch()`, `fuword*_nowatch()`, `suword*_nowatch()`, `watch_disable_addr()`, and `watch_enable_addr()` provide internal ways to perform accesses while temporarily disabling watchpoint trapping for a range.

Dependencies:
- Uses process and LWP state from `proc_t`, `klwp_t`, `lwp_watch`, `p_warea`, `p_wprot`, `p_maplock`, and `p_mapcnt`.
- Uses address-space and segment APIs: `as_segat`, `AS_LOCK_ENTER`, `SEGOP_GETPROT`, `SEGOP_SETPROT`, `seg_rw`, and VM protection flags.
- Uses procfs/watchpoint types and trap codes from `sys/procfs.h`, `sys/watchpoint.h`, and fault/signal infrastructure.
- Wraps low-level copy helpers such as `copyin_noerr`, `copyout_noerr`, `copyinstr_noerr`, `copyoutstr_noerr`, `fuword*_noerr`, and `suword*_noerr`.
- Interacts with scheduler/stop logic through `holdwatch()`, `stop()`, `continuelwps()`, `prstep()`, `ISSIG_FAST()`, and `schedctl_finish_sigblock()`.

Research notes:
- Page remapping pairs are nestable; correctness depends on `wp_kmap[]`/`wp_umap[]` reference counts and paired `pr_mappage()`/`pr_unmappage()` calls.
- The implementation explicitly compensates for MMU limitations by mapping execute and write requests with read permission as needed.
- `pr_is_watchpoint()` may adjust the fault address to the first watched byte inside a larger fault/copy range.
- Copy wrappers return `EFAULT` when watchpoint processing is aborted, when the debugger does not clear the condition, or when `lwp_sysabort` is set.
- The `watch_copyin()` parameter names are misleading relative to normal copyin direction, but it forwards to `watch_xcopyin()` and participates in the copyops vector contract.
