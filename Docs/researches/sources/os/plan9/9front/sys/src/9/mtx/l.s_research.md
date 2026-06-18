# File Research: sources/os/plan9/9front/sys/src/9/mtx/l.s

This is the MTX PowerPC low-level assembly file. It implements boot entry, initial BAT/MMU setup, FP initialization, interrupt priority controls, context-label operations, user entry, cache flushes, atomic operations, SPR accessors, TLB flushes, trap vector save/restore, and FP save/restore.

`start` configures MSR, clears interrupt/prefix state, sets early SB, calls `mmuinit0`, receives `memsize` from the ROM/debugger, initializes FP constants, sets up `mach0`, and calls `main`. `mmuinit0` invalidates TLBs, programs BATs for direct kernel mappings and I/O, enables instruction/data MMU, and returns in virtual mode.

The trap path is `trapvec` -> `saveureg` -> C `trap` -> `restoreureg`. It handles user vs kernel stack selection while traps arrive with MMU disabled, saves registers into a `Ureg`, re-enables MMU, and restores state with `RFI`. `forkret` branches into `restoreureg`.

The file also provides `fpsave`/`fprestore`, which must match `FPsave` in `dat.h`, and low-level hardware helpers such as `getdec`, `putdec`, `getdar`, `getdsisr`, `putsdr1`, `putsr`, `gethid0`, `puthid0`, `eieio`, and `sync`.

Filesystem relevance is core OS substrate: user/kernel transitions, page faults, scheduler context, and cache/TLB behavior all affect file servers and memory-mapped I/O.

Notable risks: trap entry depends on precise physical/virtual address transitions; `Mach` and `Ureg` offsets are assembly-coupled; BAT mapping assumptions are platform-specific.
