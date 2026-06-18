# File Research: sources/os/bsd/netbsd-src/sys/kern/uipc_domain.c

This file implements NetBSD's protocol domain registry, generic protocol lookup, sockaddr helpers, PF_LOCAL sysctl enumeration, and global protocol timer dispatch. It owns the global `domains` STAILQ, a fast `domain_array[AF_MAX]` lookup cache, the `M_SOCKADDR` malloc type, and the `pffasttimo`/`pfslowtimo` callouts plus monotonic tick counters.

Initialization runs through `domaininit(bool attach)`: it creates the `net.local` sysctl subtree, walks the linker-set `domains`, attaches every domain except PF_ROUTE first, then attaches PF_ROUTE last and starts protocol timers. `domaininit_post()` exists for boot paths that call `domaininit(false)` and attach domains later. `domain_attach()` inserts the domain, fills the array cache, calls domain and per-protocol init hooks, attaches mbuf owners under `MBUFTRACE`, and recomputes `max_hdr`/`max_datalen`.

Lookup APIs are `pffinddomain`, `pffindtype`, and `pffindproto`; `pffindproto` special-cases raw sockets by allowing a zero-protocol raw protosw fallback. Sockaddr routines delegate family-specific behavior through `struct domain` hooks where present: address extraction, externalization, comparison, any-address lookup, allocation/copy/dup/free, known-family size lookup, and human-readable formatting for AF_LOCAL/INET/INET6/LINK/APPLETALK.

The PF_LOCAL sysctl support is notable because there is no central local-socket PCB list. `sysctl_unpcblist()` walks the global file list, filters socket files by family/type, authorizes visibility with kauth, temporarily references each file, and serializes `struct kinfo_pcb` via `sysctl_dounpcb()`. Address exposure is guarded with `get_expose_address()`.

Control input and timers are broad fan-out mechanisms: `pfctlinput()` calls every protocol's `pr_ctlinput`; `pfctlinput2()` first narrows by sockaddr family; `pfslowtimo()` and `pffasttimo()` call protocol slow/fast timers and reschedule at `PR_SLOWHZ`/`PR_FASTHZ`.

Key dependencies: `sys/domain.h`, `sys/protosw.h`, `sys/socketvar.h`, `sys/unpcb.h`, `sys/sysctl.h`, AF-specific formatting helpers from network stacks. Risks center on global list traversal, sockaddr length correctness, and lock/ref correctness while enumerating the file list for sysctl.
