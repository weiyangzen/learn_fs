# File Research: sources/os/plan9/9front/sys/src/9/mt7688/l.s

This is the main MIPS assembly support file for the MT7688 kernel. It includes MIPS 24K macros and implements boot entry, exception vectors, interrupt priority manipulation, process context helpers, TLB helpers, cache flushing, atomic primitives, CP0 accessors, and the low-level trap save/restore path.

`start` disables interrupts, verifies a sanity word, clears compare/cause state, disables watchdog/reset behavior, configures cache mode, initializes `Mach` and BSS, initializes registers, sets `up` nil, and calls `main`. `touser` sets EPC/status and executes `ERET` into user mode.

The exception path includes `utlbmiss`, a fast software-TLB lookup using the same hash as `mmu.c`, fallback to `gevector`, full `saveregs`, dispatch to `trap` or `syscall`, and `restregs`/`forkret` return. The assembly Ureg layout is explicitly documented in comments and must match `ureg.h`.

TLB functions include `getwired`, `setwired`, `getrandom`, `getpagemask`, `setpagemask`, `puttlbx`, `gettlbx`, `gettlbp`, `gettlbvirt`, `tlbvirt`, and `stlbhash`. Cache functions include `cleancache`, `icflush`, and `dcflush`. Atomic operations are `tas` and `cmpswap` using LL/SC. CP0 accessors include `prid`, count/compare, status/cause/config, watch registers, and debug/config selector reads.

Filesystem relevance is core infrastructure: page faults, copy-on-write, user/kernel transitions, interrupt handling, and cache/TLB consistency all depend on this file. Filesystem servers and page-cache operations rely on correct Ureg save/restore and MMU refill behavior.

Notable risks: several debug or degenerate FPU routines are stubs; early boot and vector copying are highly address-layout sensitive; the fast UTLB refill path must remain exactly consistent with `mmu.c`’s `Softtlb` layout and `stlbhash`.
