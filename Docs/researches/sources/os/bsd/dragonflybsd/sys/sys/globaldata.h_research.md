# File Research: sources/os/bsd/dragonflybsd/sys/sys/globaldata.h

`globaldata.h` defines DragonFly's per-CPU `struct globaldata` for kernel and structure-visible builds. The comment notes that assembler offset generation and module/kernel compatibility depend on this layout.

The structure tracks current/free threads, run queues, CPU IDs/masks, interrupt nesting, VM counters and totals, IPI queues, scheduler/timer state, slab allocator state, vm_map_entry cache, pipe/namecache/sysid caches, tsleep hash, spinlock state, systimer state, vnode counters, debug fields, delayed wakeups, sampling PCs/SPs, per-CPU vmstats, callouts, indefinite-wait state, sysctl lock, and existential-lock counters.

The file defines request flag bit positions/masks such as `RQF_IPIQ`, `RQF_TIMER`, AST masks, scheduler/idle masks, HVM masks, globaldata flags, debug macros, and kernel prototypes `globaldata_find()` and `is_globaldata_space()`.
